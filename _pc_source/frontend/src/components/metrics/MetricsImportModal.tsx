import React, { useEffect, useState } from 'react';
import { createManualMetric, importSalesCsv } from '../../api/client';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onRefresh: () => void;
  availableSkus?: Array<{ sku_id: string; title: string }>;
}

export const MetricsImportModal: React.FC<Props> = ({ isOpen, onClose, onRefresh, availableSkus = [] }) => {
  const [activeTab, setActiveTab] = useState<'csv' | 'manual'>('csv');
  const [csvSource, setCsvSource] = useState<'gumroad' | 'hotmart'>('gumroad');
  const [csvText, setCsvText] = useState('');
  const [manualPlatform, setManualPlatform] = useState<'threads' | 'pinterest'>('threads');
  const [pieceId, setPieceId] = useState('');
  const [skuId, setSkuId] = useState('E01');
  const [impressions, setImpressions] = useState(500);
  const [clicks, setClicks] = useState(15);
  const [saves, setSaves] = useState(4);
  const [metricDate, setMetricDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [feedback, setFeedback] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      setCsvText(String(evt.target?.result || ''));
      setFeedback(`Archivo cargado: ${file.name} (${file.size} bytes)`);
    };
    reader.readAsText(file);
  };

  const handleImportCsv = async () => {
    if (!csvText.trim()) {
      setFeedback('Error: Pega o sube un archivo CSV con ventas.');
      return;
    }
    setLoading(true);
    setFeedback(null);
    try {
      const res = await importSalesCsv(csvSource, csvText);
      setFeedback(`Exito: ${String(res.imported_count ?? 0)} ventas importadas ($${String(res.total_amount_usd ?? 0)} USD)`);
      window.setTimeout(() => {
        onRefresh();
        onClose();
      }, 1200);
    } catch (error) {
      setFeedback(`Fallo de importacion: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setLoading(false);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setFeedback(null);
    try {
      await createManualMetric({
        date: metricDate,
        platform: manualPlatform,
        piece_id: pieceId.trim() || `th_${Date.now().toString().slice(-4)}`,
        sku_id: skuId || undefined,
        impressions: Number(impressions),
        clicks: Number(clicks),
        saves: Number(saves),
      });
      setFeedback('Exito: Metrica manual registrada.');
      window.setTimeout(() => {
        onRefresh();
        onClose();
      }, 1000);
    } catch (error) {
      setFeedback(`Error: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-4 font-ui" role="presentation" onClick={onClose}>
      <div role="dialog" aria-modal="true" aria-label="Ingreso de métricas reales" className="bg-[#0e1017] border border-white/10 rounded-2xl max-w-lg w-full p-5 space-y-4 shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono-tech px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-bold">DATOS REALES</span>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-grotesque">Ingreso de Metricas Reales</h3>
          </div>
          <button type="button" aria-label="Cerrar" onClick={onClose} className="text-xs text-zinc-400 hover:text-white font-mono-tech">CERRAR</button>
        </div>

        <div className="flex gap-2 p-1 bg-black/60 rounded-xl border border-white/[0.06] text-xs font-mono-tech" role="tablist" aria-label="Modo de ingreso">
          <button type="button" role="tab" aria-selected={activeTab === 'csv'} onClick={() => setActiveTab('csv')} className={`flex-1 py-1.5 rounded-lg transition font-bold ${activeTab === 'csv' ? 'bg-zinc-800 text-emerald-400' : 'text-zinc-400 hover:text-zinc-200'}`}>Importar CSV Ventas</button>
          <button type="button" role="tab" aria-selected={activeTab === 'manual'} onClick={() => setActiveTab('manual')} className={`flex-1 py-1.5 rounded-lg transition font-bold ${activeTab === 'manual' ? 'bg-zinc-800 text-[#E07A5F]' : 'text-zinc-400 hover:text-zinc-200'}`}>Metrica Manual Pieza</button>
        </div>

        {feedback && (
          <div className={`p-2.5 rounded-xl text-xs font-mono-tech border ${feedback.startsWith('Error') || feedback.startsWith('Fallo') ? 'bg-rose-950/40 text-rose-300 border-rose-500/40' : 'bg-emerald-950/40 text-emerald-300 border-emerald-500/40'}`}>
            {feedback}
          </div>
        )}

        {activeTab === 'csv' ? (
          <div className="space-y-3 text-xs">
            <div className="flex items-center gap-3">
              <span className="text-zinc-400 font-mono-tech text-[11px]">Pasarela de origen:</span>
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input type="radio" name="source" checked={csvSource === 'gumroad'} onChange={() => setCsvSource('gumroad')} />
                <span className={csvSource === 'gumroad' ? 'text-[#FF90E8] font-bold' : 'text-zinc-400'}>Gumroad (USD)</span>
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input type="radio" name="source" checked={csvSource === 'hotmart'} onChange={() => setCsvSource('hotmart')} />
                <span className={csvSource === 'hotmart' ? 'text-amber-400 font-bold' : 'text-zinc-400'}>Hotmart (LatAm/COP)</span>
              </label>
            </div>

            <div className="p-2.5 rounded-xl bg-black/60 border border-white/[0.06] text-[11px] text-zinc-400 font-mono-tech space-y-1">
              <div className="text-zinc-300 font-bold">Columnas esperadas de exportacion:</div>
              {csvSource === 'gumroad' ? (
                <div>Gumroad: <code>Order ID</code>, <code>Date</code>, <code>Product Name</code>, <code>Price</code>, <code>Currency</code></div>
              ) : (
                <div>Hotmart: <code>Codigo de transaccion</code>, <code>Fecha</code>, <code>Producto</code>, <code>Precio</code>, <code>Moneda</code></div>
              )}
            </div>

            <div className="space-y-1.5">
              <label htmlFor="metrics-csv-file" className="text-[11px] text-zinc-400 font-mono-tech block">Seleccionar archivo .CSV:</label>
              <input id="metrics-csv-file" type="file" accept=".csv,text/csv,text/plain" onChange={handleFileUpload} className="w-full text-xs text-zinc-300 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-zinc-800 file:text-emerald-400 file:font-mono-tech hover:file:bg-zinc-700 cursor-pointer" />
            </div>

            <div className="space-y-1">
              <label htmlFor="metrics-csv-text" className="text-[11px] text-zinc-400 font-mono-tech block">O pegar contenido CSV directamente:</label>
              <textarea id="metrics-csv-text" rows={4} value={csvText} onChange={(e) => setCsvText(e.target.value)} placeholder="Order ID,Date,Product Name,Price,Currency..." className="w-full bg-black/80 border border-white/10 rounded-xl p-2.5 text-xs font-mono-tech text-zinc-200 focus:outline-none focus:border-emerald-500" />
            </div>

            <button type="button" onClick={handleImportCsv} disabled={loading} className="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-mono-tech font-bold text-xs uppercase tracking-wider transition disabled:opacity-50">
              {loading ? 'Procesando Ventas...' : 'Procesar e Importar Ventas'}
            </button>
          </div>
        ) : (
          <form onSubmit={handleManualSubmit} className="space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label htmlFor="metric-platform" className="text-[11px] text-zinc-400 font-mono-tech block mb-1">Plataforma:</label>
                <select id="metric-platform" value={manualPlatform} onChange={(e) => setManualPlatform(e.target.value as 'threads' | 'pinterest')} className="w-full bg-black border border-white/10 rounded-lg p-2 text-xs font-mono-tech text-white">
                  <option value="threads">Threads</option>
                  <option value="pinterest">Pinterest</option>
                </select>
              </div>
              <div>
                <label htmlFor="metric-date" className="text-[11px] text-zinc-400 font-mono-tech block mb-1">Fecha:</label>
                <input id="metric-date" type="date" value={metricDate} onChange={(e) => setMetricDate(e.target.value)} className="w-full bg-black border border-white/10 rounded-lg p-2 text-xs font-mono-tech text-white" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label htmlFor="metric-piece" className="text-[11px] text-zinc-400 font-mono-tech block mb-1">ID Pieza (Ej: th_001):</label>
                <input id="metric-piece" type="text" value={pieceId} onChange={(e) => setPieceId(e.target.value)} placeholder="th_001 o pin_002" className="w-full bg-black border border-white/10 rounded-lg p-2 text-xs font-mono-tech text-white" />
              </div>
              <div>
                <label htmlFor="metric-sku" className="text-[11px] text-zinc-400 font-mono-tech block mb-1">SKU Vinculado:</label>
                <select id="metric-sku" value={skuId} onChange={(e) => setSkuId(e.target.value)} className="w-full bg-black border border-white/10 rounded-lg p-2 text-xs font-mono-tech text-white">
                  {availableSkus.length > 0 ? (
                    availableSkus.map((s) => (<option key={s.sku_id} value={s.sku_id}>{s.sku_id} - {s.title.slice(0, 24)}</option>))
                  ) : (
                    <option value="">Sin catálogo cargado</option>
                  )}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <div>
                <label htmlFor="metric-impresiones" className="text-[10px] text-zinc-400 font-mono-tech block mb-1">Impresiones:</label>
                <input id="metric-impresiones" type="number" min={0} value={impressions} onChange={(e) => setImpressions(Number(e.target.value))} className="w-full bg-black border border-white/10 rounded-lg p-2 text-xs font-mono-tech text-white" />
              </div>
              <div>
                <label htmlFor="metric-clics" className="text-[10px] text-zinc-400 font-mono-tech block mb-1">Clics Salientes:</label>
                <input id="metric-clics" type="number" min={0} value={clicks} onChange={(e) => setClicks(Number(e.target.value))} className="w-full bg-black border border-white/10 rounded-lg p-2 text-xs font-mono-tech text-white" />
              </div>
              <div>
                <label htmlFor="metric-saves" className="text-[10px] text-zinc-400 font-mono-tech block mb-1">Saves / Guardados:</label>
                <input id="metric-saves" type="number" min={0} value={saves} onChange={(e) => setSaves(Number(e.target.value))} className="w-full bg-black border border-white/10 rounded-lg p-2 text-xs font-mono-tech text-white" />
              </div>
            </div>

            <button type="submit" disabled={loading} className="w-full py-2.5 rounded-xl bg-[#E07A5F] hover:bg-[#d0694e] text-black font-mono-tech font-bold text-xs uppercase tracking-wider transition disabled:opacity-50">
              {loading ? 'Guardando Metrica...' : 'Guardar Metrica Real'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
