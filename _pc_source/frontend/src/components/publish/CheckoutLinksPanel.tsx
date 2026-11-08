import React, { useEffect, useMemo, useState } from 'react';
import { errorMessage, isPendingError } from '../../api/client';
import { saveCheckoutBulk, saveSkuCheckout } from '../../api/publish';
import type { CheckoutBulkResponse, ProductSKU } from '../../types/domain';
import { parseCheckoutLinks, validateCheckoutUrl } from './checkoutParse';
import { InlineError, PendingNotice, Section } from './publishUi';

interface Props {
  products: ProductSKU[];
  paidCount: number;
  readyCount: number;
  onSaved: () => void;
}

const BULK_EXAMPLE = `{
  "E01": { "gumroad_url": "https://samuel.gumroad.com/l/e01", "hotmart_url": "" },
  "E02": { "hotmart_url": "https://pay.hotmart.com/E02" }
}`;
const isReady = (sku: ProductSKU): boolean =>
  sku.checkout_ready ?? Boolean(sku.gumroad_url || sku.hotmart_url);

export const CheckoutLinksPanel: React.FC<Props> = ({ products, paidCount, readyCount, onSaved }) => {
  const paid = useMemo(() => products.filter((p) => p.price_usd > 0), [products]);
  const missing = useMemo(() => paid.filter((p) => !isReady(p)), [paid]);
  const [selectedSku, setSelectedSku] = useState('');
  const [gumroad, setGumroad] = useState('');
  const [hotmart, setHotmart] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [savePending, setSavePending] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [bulkText, setBulkText] = useState('');
  const [bulkSaving, setBulkSaving] = useState(false);
  const [bulkError, setBulkError] = useState<string | null>(null);
  const [bulkPending, setBulkPending] = useState(false);
  const [bulkErrors, setBulkErrors] = useState<string[]>([]);
  const [bulkResult, setBulkResult] = useState<CheckoutBulkResponse | null>(null);

  const current = paid.find((p) => p.sku_id === selectedSku) ?? missing[0] ?? paid[0];

  useEffect(() => {
    if (!current) return;
    setSelectedSku(current.sku_id);
    setGumroad(current.gumroad_url ?? '');
    setHotmart(current.hotmart_url ?? '');
    setSaveError(null);
    setSaveMessage(null);
  }, [current]);

  const handleSave = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!current) return;
    const gError = validateCheckoutUrl(gumroad, 'gumroad');
    const hError = validateCheckoutUrl(hotmart, 'hotmart');
    if (gError || hError) {
      setSaveError([gError, hError].filter(Boolean).join(' '));
      return;
    }
    setSaving(true);
    setSaveError(null);
    setSavePending(false);
    setSaveMessage(null);
    try {
      await saveSkuCheckout(current.sku_id, {
        gumroad_url: gumroad.trim(),
        hotmart_url: hotmart.trim(),
      });
      setSaveMessage(
        gumroad.trim() || hotmart.trim()
          ? `Checkout de ${current.sku_id} guardado.`
          : `Checkout de ${current.sku_id} borrado (se enviaron URLs vacías).`
      );
      onSaved();
    } catch (error) {
      setSavePending(isPendingError(error));
      setSaveError(errorMessage(error));
    } finally {
      setSaving(false);
    }
  };

  const handleBulk = async () => {
    const parsed = parseCheckoutLinks(bulkText);
    setBulkErrors(parsed.errors);
    setBulkResult(null);
    setBulkError(null);
    setBulkPending(false);
    if (parsed.errors.length > 0 && Object.keys(parsed.links).length === 0) return;
    setBulkSaving(true);
    try {
      const res = await saveCheckoutBulk(parsed.links);
      setBulkResult(res);
      onSaved();
    } catch (error) {
      setBulkPending(isPendingError(error));
      setBulkError(errorMessage(error));
    } finally {
      setBulkSaving(false);
    }
  };

  return (
    <Section
      title="Checkout por SKU"
      subtitle="Guarda las URLs reales de Gumroad/Hotmart. Sin checkout configurado el SKU no se puede vender."
      badge={
        <span
          className={`px-2 py-0.5 rounded-full border text-[10px] font-mono-tech font-bold tabular-nums ${
            missing.length === 0
              ? 'bg-emerald-950/50 border-emerald-500/40 text-emerald-300'
              : 'bg-amber-500/[0.08] border-amber-500/40 text-amber-300'
          }`}
        >
          {missing.length} de {paidCount || paid.length} sin checkout
        </span>
      }
    >
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <form onSubmit={handleSave} className="space-y-2.5 bg-black/30 border border-white/[0.07] rounded-xl p-3">
          <div className="text-[10px] uppercase tracking-wider text-zinc-400 font-mono-tech font-bold">Un SKU</div>
          <div>
            <label htmlFor="checkout-sku" className="block text-[10px] text-zinc-400 mb-1">SKU de pago</label>
            <select
              id="checkout-sku"
              value={current?.sku_id ?? ''}
              onChange={(e) => setSelectedSku(e.target.value)}
              className="w-full bg-black border border-zinc-800 rounded-lg px-2.5 py-1.5 text-xs text-zinc-200"
            >
              {paid.map((p) => (
                <option key={p.sku_id} value={p.sku_id}>
                  {p.sku_id} - {p.title} {isReady(p) ? '(con checkout)' : '(sin checkout)'}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="checkout-gumroad" className="block text-[10px] text-zinc-400 mb-1">URL Gumroad (https)</label>
            <input
              id="checkout-gumroad"
              type="url"
              inputMode="url"
              value={gumroad}
              onChange={(e) => setGumroad(e.target.value)}
              placeholder="https://tu-usuario.gumroad.com/l/sku"
              className="w-full bg-black border border-zinc-800 rounded-lg px-2.5 py-1.5 text-xs text-zinc-200 placeholder:text-zinc-600"
            />
          </div>
          <div>
            <label htmlFor="checkout-hotmart" className="block text-[10px] text-zinc-400 mb-1">URL Hotmart (https)</label>
            <input
              id="checkout-hotmart"
              type="url"
              inputMode="url"
              value={hotmart}
              onChange={(e) => setHotmart(e.target.value)}
              placeholder="https://pay.hotmart.com/XXXX"
              className="w-full bg-black border border-zinc-800 rounded-lg px-2.5 py-1.5 text-xs text-zinc-200 placeholder:text-zinc-600"
            />
          </div>
          <button
            type="submit"
            disabled={saving || !current}
            className="w-full py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black text-[11px] font-mono-tech font-bold transition disabled:opacity-50"
          >
            {saving ? 'Guardando...' : 'Guardar checkout'}
          </button>
          {savePending && <PendingNotice endpoint={`/api/catalog/${current?.sku_id ?? 'SKU'}/checkout`} />}
          {!savePending && saveError && <InlineError message={saveError} />}
          {saveMessage && (
            <div className="p-2 rounded-lg bg-emerald-500/[0.07] border border-emerald-500/30 text-[11px] text-emerald-200">{saveMessage}</div>
          )}
          <p className="text-[10px] text-zinc-500 leading-relaxed">
            Guardar con ambos campos vacíos borra el checkout del SKU. El backend valida https y host permitido.
          </p>
        </form>

        <div className="space-y-2.5 bg-black/30 border border-white/[0.07] rounded-xl p-3">
          <div className="flex items-center justify-between">
            <div className="text-[10px] uppercase tracking-wider text-zinc-400 font-mono-tech font-bold">Pegar en bloque</div>
            <span className="text-[10px] text-zinc-500 font-mono-tech tabular-nums">{readyCount} listos</span>
          </div>
          <label htmlFor="checkout-bulk" className="block text-[10px] text-zinc-400">
            JSON o líneas <code className="text-zinc-300">SKU,URL</code>
          </label>
          <textarea
            id="checkout-bulk"
            value={bulkText}
            onChange={(e) => setBulkText(e.target.value)}
            rows={7}
            spellCheck={false}
            placeholder={BULK_EXAMPLE}
            className="w-full bg-black border border-zinc-800 rounded-lg px-2.5 py-2 text-[11px] text-zinc-200 font-mono-tech leading-relaxed placeholder:text-zinc-700 resize-y"
          />
          <button
            type="button"
            onClick={handleBulk}
            disabled={bulkSaving || bulkText.trim().length === 0}
            className="w-full py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black text-[11px] font-mono-tech font-bold transition disabled:opacity-50"
          >
            {bulkSaving ? 'Aplicando...' : 'Aplicar checkout en bloque'}
          </button>
          {bulkPending && <PendingNotice endpoint="/api/catalog/checkout-bulk" />}
          {!bulkPending && bulkError && <InlineError message={bulkError} />}
          {bulkErrors.length > 0 && (
            <ul className="space-y-0.5 text-[10px] text-rose-200 max-h-24 overflow-y-auto">
              {bulkErrors.map((message, index) => (
                <li key={`${index}-${message}`} className="leading-relaxed">{message}</li>
              ))}
            </ul>
          )}
          {bulkResult && (
            <div className="p-2 rounded-lg bg-emerald-500/[0.07] border border-emerald-500/30 text-[11px] text-emerald-200 leading-relaxed">
              Actualizados: <b className="tabular-nums">{bulkResult.updated ?? 0}</b> · Omitidos:{' '}
              <b className="tabular-nums">{bulkResult.skipped ?? 0}</b> · Errores:{' '}
              <b className="tabular-nums">{bulkResult.errors?.length ?? 0}</b>
              {bulkResult.errors && bulkResult.errors.length > 0 && (
                <ul className="mt-1 space-y-0.5 text-[10px] text-rose-200 max-h-20 overflow-y-auto">
                  {bulkResult.errors.slice(0, 5).map((item, index) => (
                    <li key={`${index}-${item.sku_id ?? 'err'}`}>{item.sku_id ? `${item.sku_id}: ` : ''}{item.reason ?? 'error de validación'}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </div>

      {missing.length > 0 && (
        <div className="space-y-1">
          <div className="text-[10px] uppercase tracking-wider text-amber-300 font-mono-tech font-bold">
            SKUs de pago sin checkout ({missing.length})
          </div>
          <div className="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto">
            {missing.map((sku) => (
              <button
                key={sku.sku_id}
                type="button"
                onClick={() => setSelectedSku(sku.sku_id)}
                className="px-1.5 py-0.5 rounded bg-black border border-amber-500/30 text-amber-200 font-mono-tech text-[10px] hover:border-amber-400 transition"
                title={`Configurar checkout de ${sku.sku_id}`}
              >
                {sku.sku_id}
              </button>
            ))}
          </div>
        </div>
      )}
    </Section>
  );
};
