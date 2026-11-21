"use client";

import { CheckCircle2, LoaderCircle, RotateCcw, X } from "lucide-react";
import { useState } from "react";
import styles from "./CostReceipt.module.css";

type ReceiptModel = { id: string; name: string; tokens: number; cost: number };

const money = (amount: number) => `$${amount.toFixed(6)}`;

export default function CostReceipt({
  runName,
  models,
  judgeCost,
  onClose,
}: {
  runName: string;
  models: ReceiptModel[];
  judgeCost: number;
  onClose: () => void;
}) {
  const [printKey, setPrintKey] = useState(0);
  const total = models.reduce((sum, model) => sum + model.cost, 0) + judgeCost;
  const tokens = models.reduce((sum, model) => sum + model.tokens, 0);

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/75 p-4 backdrop-blur-sm" onClick={onClose}>
      <div role="dialog" aria-modal="true" aria-labelledby="cost-receipt-title" className="my-auto w-full max-w-md" onClick={(event) => event.stopPropagation()}>
        <div className="mb-3 flex items-center justify-between text-white">
          <h2 id="cost-receipt-title" className="text-lg font-semibold">Cost Details</h2>
          <div className="flex items-center gap-1">
            <button type="button" onClick={() => setPrintKey((key) => key + 1)} className="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs text-slate-300 hover:bg-slate-800 hover:text-white" aria-label="Replay receipt printing"><RotateCcw size={14} /> Replay</button>
            <button type="button" autoFocus onClick={onClose} aria-label="Close cost details" className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white"><X size={20} /></button>
          </div>
        </div>
        <div key={printKey} className={styles.printer}>
          <div className={styles.machine}>
            <div className={styles.machineHeader}><span>TOKENLENS</span><span className={styles.light} /></div>
            <div className={styles.screen}>
              <span className={styles.screenLabel}>RUN COST</span>
              <strong>{money(total)}</strong>
              <span>Receipt for {runName}</span>
              <div className={styles.status} aria-hidden="true">
                <span className={`${styles.statusStep} ${styles.preparing}`}><LoaderCircle className={styles.spinner} size={16} /> Preparing receipt</span>
                <span className={`${styles.statusStep} ${styles.printing}`}><LoaderCircle className={styles.spinner} size={16} /> Printing receipt</span>
                <span className={`${styles.statusStep} ${styles.complete}`}><CheckCircle2 size={16} /> Receipt ready</span>
              </div>
            </div>
            <div className={styles.slot} />
          </div>
          <div className={styles.output}>
            <div className={styles.slotShadow} aria-hidden="true" />
            <article className={styles.paper}>
              <div className={styles.receiptHeader}>
                <strong>TokenLens</strong>
                <span>RUN COST DETAILS</span>
              </div>
              <p className={styles.runName}>{runName}</p>
              <div className={styles.divider} />
              {models.map((model) => (
                <div key={model.id} className={styles.item}>
                  <div className={styles.line}><strong>{model.name}</strong><strong>{money(model.cost)}</strong></div>
                  <span>{model.tokens.toLocaleString()} tokens</span>
                </div>
              ))}
              {judgeCost > 0 && (
                <div className={styles.item}>
                  <div className={styles.line}><strong>Judge</strong><strong>{money(judgeCost)}</strong></div>
                  <span>Judge token counts unavailable</span>
                </div>
              )}
              <div className={styles.divider} />
              <div className={styles.line}><span>Model tokens</span><strong>{tokens.toLocaleString()}</strong></div>
              <div className={`${styles.line} ${styles.total}`}><strong>Total</strong><strong>{money(total)}</strong></div>
              <p className={styles.footer}>USD · Saved usage</p>
            </article>
          </div>
        </div>
      </div>
    </div>
  );
}
