 backend/app/__init__.py => TestAzure.py       |   0
 backend/TestDBRender.py                       |  29 [32m+++[m
 backend/alembic/env.py                        |   6 [32m+[m[31m-[m
 backend/app/config.py                         |  11 [32m+[m[31m-[m
 backend/app/controllers/auth_controller.py    | 102 [32m++++++++[m
 backend/app/controllers/dataset_controller.py | 315 [32m++++++++++++++++++++++[m
 backend/app/controllers/model_controller.py   | 161 [32m++++++++++++[m
 backend/app/controllers/rubric_controller.py  | 140 [32m++++++++++[m
 backend/app/controllers/run_controller.py     | 166 [32m++++++++++++[m
 backend/app/controllers/user_controller.py    |  60 [32m+++++[m
 backend/app/dbconfig.py                       |  45 [32m++++[m
 backend/app/main.py                           |  46 [32m+++[m[31m-[m
 backend/app/models/dataset.py                 |  35 [32m+++[m
 backend/app/models/dataset_item.py            |  29 [32m+++[m
 backend/app/models/entities.py                |  29 [32m+++[m
 backend/app/models/enums.py                   |  29 [32m+++[m
 backend/app/models/judgment.py                |  37 [32m+++[m
 backend/app/models/model.py                   |  48 [32m++++[m
 backend/app/models/regression_alert.py        |  34 [32m+++[m
 backend/app/models/result.py                  |  49 [32m++++[m
 backend/app/models/rubric.py                  |  31 [32m+++[m
 backend/app/models/run.py                     |  66 [32m+++++[m
 backend/app/models/run_model.py               |  23 [32m++[m
 backend/app/models/user.py                    |  32 [32m+++[m
 backend/app/schemas/auth_schema.py            |  35 [32m+++[m
 backend/app/schemas/dataset_schema.py         |  77 [32m++++++[m
 backend/app/schemas/model_schema.py           |  37 [32m+++[m
 backend/app/schemas/rubric_schema.py          |  37 [32m+++[m
 backend/app/schemas/run_schema.py             |  84 [32m++++++[m
 backend/app/services/auth_service.py          | 151 [32m+++++++++++[m
 backend/app/services/dataset_service.py       | 362 [32m++++++++++++++++++++++++++[m
 backend/app/services/model_service.py         |  98 [32m+++++++[m
 backend/app/services/rubric_service.py        | 118 [32m+++++++++[m
 backend/app/services/run_service.py           | 188 [32m+++++++++++++[m
 backend/app/services/user_service.py          |  22 [32m++[m
 backend/evaluation/__init__.py                |   1 [31m-[m
 backend/requirements.txt                      |   6 [32m+[m[31m-[m
 backend/tests/test_models.py                  | 301 [32m+++++++++++++++++++++[m
 backend/tokenlens.db                          | Bin [31m0[m -> [32m122880[m bytes
 backend/worker/__init__.py                    |   0
 40 files changed, 3028 insertions(+), 12 deletions(-)
