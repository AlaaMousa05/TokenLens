"""Schema contracts that can be checked without connecting to a database."""

import re
import unittest
import uuid

from sqlalchemy import CheckConstraint, DateTime, Numeric, UniqueConstraint, inspect
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import configure_mappers
from sqlalchemy.schema import CreateIndex, CreateTable

from app.dbconfig import Base
from app.models.entities import (
    Dataset,
    DatasetItem,
    Judgment,
    Model,
    RegressionAlert,
    Result,
    Rubric,
    Run,
    RunModel,
    User,
)


MODELS = {
    User: "users",
    Model: "models",
    Dataset: "datasets",
    DatasetItem: "dataset_items",
    Rubric: "rubrics",
    Run: "runs",
    RunModel: "run_models",
    Result: "results",
    Judgment: "judgments",
    RegressionAlert: "regression_alerts",
}

COLUMNS = {
    User: "id name email password_hash role created_at",
    Model: "id provider model_name display_name input_price_per_mtok output_price_per_mtok context_window is_active updated_at",
    Dataset: "id owner_id name description source_format is_golden created_at",
    DatasetItem: "id dataset_id position input_prompt expected_output metadata",
    Rubric: "id owner_id name criteria scale_min scale_max judge_instructions created_at",
    Run: "id user_id dataset_id rubric_id baseline_run_id judge_model_id name repeats temperature swap_order status total_cost_usd created_at finished_at",
    RunModel: "run_id model_id",
    Result: "id run_id item_id model_id repeat_index output_text input_tokens output_tokens latency_ms cost_usd status error_message attempts created_at",
    Judgment: "id result_id judge_model_id order_variant score criteria_scores reasoning judge_cost_usd created_at",
    RegressionAlert: "id run_id baseline_run_id model_id baseline_score new_score delta threshold created_at",
}

FOREIGN_KEYS = {
    Dataset: {"owner_id": "users.id"},
    DatasetItem: {"dataset_id": "datasets.id"},
    Rubric: {"owner_id": "users.id"},
    Run: {
        "user_id": "users.id",
        "dataset_id": "datasets.id",
        "rubric_id": "rubrics.id",
        "baseline_run_id": "runs.id",
        "judge_model_id": "models.id",
    },
    RunModel: {"run_id": "runs.id", "model_id": "models.id"},
    Result: {"run_id": "runs.id", "item_id": "dataset_items.id", "model_id": "models.id"},
    Judgment: {"result_id": "results.id", "judge_model_id": "models.id"},
    RegressionAlert: {
        "run_id": "runs.id",
        "baseline_run_id": "runs.id",
        "model_id": "models.id",
    },
}


def compact(sql):
    return re.sub(r"\s+", " ", str(sql)).strip().lower()


class ModelSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_mappers()

    def test_models_share_metadata_and_are_mapped(self):
        for model, table_name in MODELS.items():
            with self.subTest(model=model.__name__):
                mapper = inspect(model)
                self.assertIs(mapper.local_table.metadata, Base.metadata)
                self.assertIs(Base.metadata.tables[table_name], mapper.local_table)
                self.assertTrue(mapper.primary_key)
                self.assertTrue(set(COLUMNS[model].split()).issubset(mapper.local_table.c.keys()))

    def test_foreign_keys(self):
        for model, foreign_keys in FOREIGN_KEYS.items():
            for name, target in foreign_keys.items():
                with self.subTest(model=model.__name__, column=name):
                    self.assertEqual(
                        {fk.target_fullname for fk in model.__table__.c[name].foreign_keys},
                        {target},
                    )

    def test_run_relationships_use_the_intended_foreign_keys(self):
        cases = (
            (Run, "baseline_run", Run, "baseline_run_id", "compared_runs"),
            (RegressionAlert, "run", Run, "run_id", "regression_alerts"),
            (RegressionAlert, "baseline_run", Run, "baseline_run_id", "baseline_alerts"),
            (RegressionAlert, "model", Model, "model_id", "regression_alerts"),
        )
        for model, name, target, foreign_key, inverse in cases:
            with self.subTest(model=model.__name__, relationship=name):
                relation = inspect(model).relationships[name]
                self.assertIs(relation.mapper.class_, target)
                self.assertEqual(relation.back_populates, inverse)
                self.assertEqual(
                    {(local.name, remote.name) for local, remote in relation.local_remote_pairs},
                    {(foreign_key, "id")},
                )
                self.assertEqual(inspect(target).relationships[inverse].back_populates, name)

    def test_nullability_and_defaults(self):
        nullable = (
            (DatasetItem, "expected_output"),
            (Run, "baseline_run_id"),
            (Run, "finished_at"),
            (Result, "error_message"),
        )
        for model, name in nullable:
            with self.subTest(model=model.__name__, column=name):
                self.assertTrue(model.__table__.c[name].nullable)
        for model, name, value in (
            (Model, "is_active", True),
            (Dataset, "is_golden", False),
            (Run, "swap_order", False),
        ):
            with self.subTest(model=model.__name__, column=name):
                column = model.__table__.c[name]
                self.assertFalse(column.nullable)
                self.assertIs(column.default.arg, value)
                self.assertEqual(
                    compact(column.server_default.arg.compile(dialect=postgresql.dialect())),
                    str(value).lower(),
                )
        for model in (User, Dataset, Rubric, Run, Result, Judgment, RegressionAlert):
            with self.subTest(model=model.__name__, column="created_at"):
                column = model.__table__.c.created_at
                self.assertFalse(column.nullable)
                self.assertEqual(compact(column.server_default.arg), "now()")
        self.assertEqual({column.name for column in RunModel.__table__.primary_key}, {"run_id", "model_id"})

    def test_only_specified_columns_are_nullable(self):
        nullable = {
            ("dataset_items", "expected_output"),
            ("runs", "baseline_run_id"),
            ("runs", "finished_at"),
            ("results", "error_message"),
        }
        actual = {
            (table.name, column.name)
            for table in Base.metadata.tables.values()
            for column in table.columns
            if column.nullable
        }
        self.assertEqual(actual, nullable)

    def test_uuid_timestamps_and_numeric_types(self):
        for model in MODELS:
            if model is not RunModel:
                with self.subTest(model=model.__name__, column="id"):
                    column = model.__table__.c.id
                    self.assertIsInstance(column.type, postgresql.UUID)
                    self.assertIsInstance(column.default.arg(None), uuid.UUID)
            for column in model.__table__.columns:
                if isinstance(column.type, DateTime):
                    with self.subTest(model=model.__name__, column=column.name):
                        self.assertTrue(column.type.timezone)
        numeric_columns = {
            Model: {"input_price_per_mtok": (10, 4), "output_price_per_mtok": (10, 4)},
            Run: {"temperature": (3, 2), "total_cost_usd": (12, 6)},
            Result: {"cost_usd": (12, 6)},
            Judgment: {"score": (4, 2), "judge_cost_usd": (12, 6)},
            RegressionAlert: {
                "baseline_score": (4, 2),
                "new_score": (4, 2),
                "delta": (5, 2),
                "threshold": (4, 2),
            },
        }
        for model, columns in numeric_columns.items():
            for name, precision_scale in columns.items():
                with self.subTest(model=model.__name__, column=name):
                    column_type = model.__table__.c[name].type
                    self.assertIsInstance(column_type, Numeric)
                    self.assertEqual((column_type.precision, column_type.scale), precision_scale)

    def test_relationships_do_not_cascade_historical_deletes(self):
        for table in Base.metadata.tables.values():
            for foreign_key in table.foreign_keys:
                with self.subTest(table=table.name, foreign_key=foreign_key.parent.name):
                    self.assertIsNone(foreign_key.ondelete)
        for model in MODELS:
            for relation in inspect(model).relationships:
                with self.subTest(model=model.__name__, relationship=relation.key):
                    self.assertNotIn("delete", relation.cascade)
                    if relation.direction.name == "ONETOMANY" and not relation.viewonly:
                        self.assertEqual(relation.passive_deletes, "all")

    def assert_unique_columns(self, table, columns):
        expected = tuple(columns)
        unique_keys = [
            tuple(column.name for column in constraint.columns)
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        ]
        unique_keys.extend(
            tuple(column.name for column in index.columns)
            for index in table.indexes
            if index.unique
        )
        self.assertIn(expected, unique_keys)

    def test_result_and_judgment_uniqueness(self):
        self.assert_unique_columns(User.__table__, ("email",))
        self.assert_unique_columns(Model.__table__, ("model_name",))
        self.assert_unique_columns(
            Result.__table__, ("run_id", "item_id", "model_id", "repeat_index")
        )
        self.assert_unique_columns(Judgment.__table__, ("result_id", "order_variant"))
        for table, names in (
            (Result.__table__, ("run_id", "item_id", "model_id", "repeat_index")),
            (Judgment.__table__, ("result_id", "order_variant")),
        ):
            for name in names:
                with self.subTest(table=table.name, column=name):
                    self.assertFalse(table.c[name].nullable)

    def test_order_variant_check_compiles_to_postgresql(self):
        checks = [
            compact(constraint.sqltext.compile(dialect=postgresql.dialect()))
            for constraint in Judgment.__table__.constraints
            if isinstance(constraint, CheckConstraint)
        ]
        # Equivalent SQL forms are accepted without depending on constraint names.
        allowed = (
            r"order_variant\s+in\s*\(\s*0\s*,\s*1\s*\)",
            r"order_variant\s+between\s+0\s+and\s+1",
            r"order_variant\s*=\s*0\s+or\s+order_variant\s*=\s*1",
        )
        self.assertTrue(
            any(re.fullmatch(pattern, check) for check in checks for pattern in allowed),
            checks,
        )

    def assert_index(self, table, columns, descending=None):
        matching = [
            index
            for index in table.indexes
            if tuple(column.name for column in index.columns) == tuple(columns)
        ]
        self.assertTrue(matching, (table.name, columns))
        if descending:
            self.assertTrue(
                any(
                    re.search(
                        rf"\b{re.escape(descending)}\s+desc\b",
                        compact(CreateIndex(index).compile(dialect=postgresql.dialect())),
                    )
                    for index in matching
                )
            )

    def test_required_indexes(self):
        self.assert_index(Result.__table__, ("run_id", "model_id"))
        self.assert_index(DatasetItem.__table__, ("dataset_id", "position"))
        self.assert_index(Run.__table__, ("user_id", "created_at"), "created_at")

    def test_all_tables_and_indexes_compile_for_postgresql(self):
        dialect = postgresql.dialect()
        for model, table_name in MODELS.items():
            with self.subTest(table=table_name):
                ddl = compact(CreateTable(model.__table__).compile(dialect=dialect))
                self.assertIn(f"create table {table_name}", ddl)
                for column_name in COLUMNS[model].split():
                    self.assertIn(column_name, ddl)
                for index in model.__table__.indexes:
                    self.assertIn("create", compact(CreateIndex(index).compile(dialect=dialect)))

    def test_postgresql_ddl_keeps_schema_constraints_and_types(self):
        dialect = postgresql.dialect()
        result_ddl = compact(CreateTable(Result.__table__).compile(dialect=dialect))
        judgment_ddl = compact(CreateTable(Judgment.__table__).compile(dialect=dialect))
        item_ddl = compact(CreateTable(DatasetItem.__table__).compile(dialect=dialect))
        self.assertIn("unique (run_id, item_id, model_id, repeat_index)", result_ddl)
        self.assertIn("unique (result_id, order_variant)", judgment_ddl)
        self.assertIn("check (", judgment_ddl)
        self.assertTrue("metadata jsonb" in item_ddl or "metadata json" in item_ddl)
        self.assertIn("id uuid", result_ddl)
        self.assertIn("foreign key(run_id) references runs (id)", result_ddl)


if __name__ == "__main__":
    unittest.main()
