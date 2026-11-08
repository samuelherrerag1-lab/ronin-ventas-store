import React, { useState } from 'react';
import type { ThreadsPostItem } from '../../types/domain';
import { copyText } from '../../utils/clipboard';
import { IosBaitFrame } from '../bait/IosBaitFrame';

interface Props {
  threads: ThreadsPostItem[];
  onMutateHook: (postId: string) => void;
  onToggleStatus: (postId: string) => void;
  loading?: boolean;
}

const ThreadsLogo = () => (
  <svg className="w-8 h-8 fill-white" viewBox="0 0 192 192">
    <path d="m141.5 89a66.7 66.7 0 0 0-2.5-15c-4.3-15.1-15.2-26.8-29.4-31.4-19.2-6.3-41.3-.6-54.7 14-13.4 14.6-16.7 35.8-8.3 53.6 8.4 17.8 26.7 28.5 46.4 27.2 12-.8 23.3-6.2 31-14.7l-10.4-9.4c-5.5 6-13.5 9.9-22 10.5-14 1-26.8-6.6-32.7-19.2-6-12.6-3.6-27.6 5.8-37.8 9.5-10.3 25-14.3 38.6-9.9 10 3.3 17.7 11.5 20.7 22.1 1.5 5.2 1.8 10.7 1 16.1-.7 4.8-2.9 9.4-6.3 12.9-3.3 3.5-7.8 5.5-12.6 5.7-5.5.2-10.6-2-14.2-6-3.6-4.1-5.1-9.6-4.1-15.2 1-5.6 4.2-10.4 8.8-13.3 4.6-2.8 10.1-3.5 15.3-2l3.4-13.3c-7.6-2.4-15.9-1.3-22.7 2.9-6.8 4.2-11.6 11.4-13 19.7-1.5 8.3.7 16.6 6.1 22.6 5.4 6 13 9.3 21.1 9 7.2-.3 13.9-3.3 18.8-8.5 5-5.2 8.3-12 9.3-19.2.9-5.9.7-11.9-.7-17.6z" />
  </svg>
);

const MetaBadge = () => (
  <svg className="w-3.5 h-3.5 fill-[#0095F6] shrink-0" viewBox="0 0 24 24">
    <path d="M10.3 2.3a2.4 2.4 0 0 1 3.4 0l1 .9a2.4 2.4 0 0 0 2.2.7l1.3-.3a2.4 2.4 0 0 1 2.8 2l.2 1.3a2.4 2.4 0 0 0 1.5 1.8l1.2.5a2.4 2.4 0 0 1 1.4 3.1l-.5 1.3a2.4 2.4 0 0 0 .3 2.3l.9 1a2.4 2.4 0 0 1-.6 3.4l-1.1.7a2.4 2.4 0 0 0-1 2.1l0 1.4a2.4 2.4 0 0 1-2.4 2.4l-1.4 0a2.4 2.4 0 0 0-2.1 1l-.7 1.1a2.4 2.4 0 0 1-3.4.6l-1-.9a2.4 2.4 0 0 0-2.3-.3l-1.3.5a2.4 2.4 0 0 1-3.1-1.4l-.5-1.2a2.4 2.4 0 0 0-1.8-1.5l-1.3-.2a2.4 2.4 0 0 1-2-2.8l.3-1.3a2.4 2.4 0 0 0-.7-2.2l-.9-1a2.4 2.4 0 0 1 0-3.4l.9-1a2.4 2.4 0 0 0 .7-2.2l-.3-1.3a2.4 2.4 0 0 1 2-2.8l1.3-.2a2.4 2.4 0 0 0 1.8-1.5l.5-1.2a2.4 2.4 0 0 1 3.1-1.4l1.3.5a2.4 2.4 0 0 0 2.3-.3l1-.9zM16.7 9.3a1 1 0 0 0-1.4-1.4l-4.3 4.3-1.6-1.6a1 1 0 0 0-1.4 1.4l2.3 2.3a1 1 0 0 0 1.4 0l5-5z" />
  </svg>
);

const HeartIcon = ({ isLiked }: { isLiked?: boolean }) => (
  <svg
    className="w-5 h-5 shrink-0 transition"
    viewBox="0 0 24 24"
    fill={isLiked ? '#FF3040' : 'none'}
    stroke={isLiked ? '#FF3040' : 'currentColor'}
    strokeWidth={1.8}
  >
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
  </svg>
);

export const ThreadsCloneView: React.FC<Props> = ({ threads, onMutateHook, onToggleStatus, loading }) => {
  const [activeTab, setActiveTab] = useState<'for_you' | 'following'>('for_you');
  const [filter, setFilter] = useState('all');
  const [slideIdx, setSlideIdx] = useState<Record<string, number>>({});
  const [likedIds, setLikedIds] = useState<Record<string, boolean>>({});
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [copyFailed, setCopyFailed] = useState(false);

  const filtered = filter === 'all' ? threads : threads.filter((t) => t.strategy_lane === filter);

  const toggleLike = (postId: string) => {
    setLikedIds((prev) => ({ ...prev, [postId]: !prev[postId] }));
  };

  const copy = (key: string, text: string) => {
    void copyText(text).then((ok) => {
      setCopyFailed(!ok);
      setCopiedId(ok ? key : null);
      window.setTimeout(() => setCopiedId(null), 1600);
    });
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#F3F5F7] py-2 px-2 sm:px-4 font-[-apple-system,BlinkMacSystemFont,'Segoe_UI',Roboto,sans-serif]">
      <div className="max-w-[620px] mx-auto pb-12">
        <div className="flex justify-center py-2 mb-2"><ThreadsLogo /></div>
        <div className="flex items-center justify-between border-b border-[#262626] pb-1 mb-3 px-1 gap-2">
          <div className="flex gap-4 sm:gap-6 text-[14px] sm:text-[15px] font-semibold shrink-0">
            {(['for_you', 'following'] as const).map((tab) => (
              <button key={tab} onClick={() => setActiveTab(tab)} className={`relative pb-3 transition whitespace-nowrap ${activeTab === tab ? 'text-white' : 'text-[#777777] hover:text-zinc-300'}`}>
                {tab === 'for_you' ? 'Para ti' : 'Siguiendo'}
                {activeTab === tab && <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-white rounded-full" />}
              </button>
            ))}
          </div>
          <div className="flex gap-1 overflow-x-auto no-scrollbar py-1 shrink min-w-0 justify-end">
            {[
              { id: 'all', label: 'Todas' },
              { id: 'via_a_captura_anzuelo', label: 'Anzuelos' },
              { id: 'via_b_ragebait_cinico', label: 'Ragebait' },
              { id: 'via_c_demo_microapp', label: 'Micro-Apps' },
            ].map((t) => (
              <button key={t.id} onClick={() => setFilter(t.id)} className={`px-2.5 py-1 text-[11px] rounded-full transition font-medium whitespace-nowrap shrink-0 ${filter === t.id ? 'bg-white text-black font-semibold' : 'bg-[#1e1e1e] text-[#777777] hover:text-zinc-300'}`}>{t.label}</button>
            ))}
          </div>
        </div>

        <div className="bg-[#181818] border border-[#262626] rounded-[20px] sm:rounded-[24px] overflow-hidden shadow-2xl">
          <div className="px-3.5 sm:px-6 py-3.5 sm:py-4 border-b border-[#262626] flex items-center justify-between gap-2">
            <div className="flex items-center gap-3 min-w-0">
              <img src="/generated_images/ron_avatar_profile.png" alt="@ronoverthinks" className="w-9 h-9 rounded-full object-cover ring-1 ring-zinc-700 shadow shrink-0" />
              <span className="text-[#777777] text-[14px] sm:text-[15px] truncate">Que hay de nuevo?</span>
            </div>
            <span className="px-3 sm:px-4 py-1.5 rounded-full bg-white/[0.06] text-zinc-400 border border-white/10 font-mono-tech text-[10px] uppercase tracking-wider shrink-0" title="La composición y el envío a Threads son manuales: esta vista es una maqueta 1:1">
              Maqueta 1:1
            </span>
          </div>

          {loading && <div className="text-center py-8 text-[#777777] animate-pulse text-xs">Sincronizando feeds con Ronin Core...</div>}
          {copyFailed && (
            <div role="alert" className="mx-3.5 sm:mx-6 mt-3 p-2 rounded-lg bg-rose-950/50 border border-rose-500/40 text-[11px] text-rose-200">
              No se pudo copiar al portapapeles. El navegador bloqueó el acceso (HTTP en LAN): selecciona el texto y copia manualmente.
            </div>
          )}

          {filtered.map((post) => {
            const currSlide = slideIdx[post.post_id] || 0;
            const isCarousel = post.format === 'carousel_dark' || post.body_slides.length > 1;
            const isLiked = !!likedIds[post.post_id];
            const likesCount = post.simulated_likes + (isLiked ? 1 : 0);

            return (
              <article key={post.post_id} className="border-b border-[#262626] px-3.5 sm:px-6 py-4 flex gap-3 hover:bg-white/[0.015] transition">
                <div className="flex flex-col items-center shrink-0">
                  <div className="relative shrink-0">
                    <img src="/generated_images/ron_avatar_profile.png" alt="@ronoverthinks" className="w-9 h-9 rounded-full object-cover ring-1 ring-zinc-700 shadow" />
                    <span className="w-4 h-4 rounded-full bg-white text-black font-bold text-[11px] flex items-center justify-center ring-2 ring-[#181818] absolute -bottom-0.5 -right-0.5 leading-none select-none">+</span>
                  </div>
                  <div className="w-[2px] bg-[#333638] my-2 flex-1 rounded-full min-h-[36px]" />
                  <div className="relative w-6 h-4 shrink-0">
                    <img src="/generated_images/ron_panic.png" alt="reply" className="w-3.5 h-3.5 rounded-full object-cover border border-[#181818] absolute left-0 top-0" />
                    <img src="/generated_images/ron_tired.png" alt="reply" className="w-3.5 h-3.5 rounded-full object-cover border border-[#181818] absolute left-2 top-0" />
                  </div>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <div className="flex items-center gap-1.5 flex-wrap min-w-0">
                      <span className="font-semibold text-[15px] text-[#F3F5F7] hover:underline cursor-pointer">ronoverthinks</span>
                      <MetaBadge />
                      <span className="text-[#777777] text-[14px]" aria-hidden="true">
                        <svg className="w-3 h-3 inline fill-current" viewBox="0 0 24 24"><path d="m9 18 6-6-6-6" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
                      </span>
                      <span className="text-[#0095F6] text-[13px] font-medium truncate">#{post.topic_tag}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[#777777] text-xs shrink-0 whitespace-nowrap">
                      <span>2 h</span>
                      <svg className="w-4 h-4 fill-current hover:text-white cursor-pointer" viewBox="0 0 24 24"><circle cx="5" cy="12" r="2" /><circle cx="12" cy="12" r="2" /><circle cx="19" cy="12" r="2" /></svg>
                    </div>
                  </div>

                  {isCarousel ? (
                    <div className="my-2 rounded-2xl border border-[#2c2c2e] bg-[#101010] p-4 text-[14px] leading-relaxed">
                      <p className="whitespace-pre-line text-[#F3F5F7]">{post.body_slides[currSlide]}</p>
                      <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-zinc-800/80 text-xs text-[#777777]">
                        <div className="flex gap-1.5 items-center">
                          {post.body_slides.map((_, i) => (
                            <span key={i} className={`h-1.5 rounded-full transition-all ${i === currSlide ? 'bg-white w-4' : 'bg-zinc-700 w-1.5'}`} />
                          ))}
                        </div>
                        <div className="flex gap-1.5">
                          <button type="button" aria-label="Slide anterior" disabled={currSlide === 0} onClick={() => setSlideIdx({ ...slideIdx, [post.post_id]: currSlide - 1 })} className="px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 disabled:opacity-25">
                            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2} aria-hidden="true"><path d="m15 18-6-6 6-6" strokeLinecap="round" strokeLinejoin="round" /></svg>
                          </button>
                          <button type="button" aria-label="Slide siguiente" disabled={currSlide === post.body_slides.length - 1} onClick={() => setSlideIdx({ ...slideIdx, [post.post_id]: currSlide + 1 })} className="px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 disabled:opacity-25">
                            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2} aria-hidden="true"><path d="m9 18 6-6-6-6" strokeLinecap="round" strokeLinejoin="round" /></svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-[15px] leading-[1.45] text-[#F3F5F7] whitespace-pre-line my-1">{post.body_slides.join('\n\n')}</div>
                  )}

                  {post.bait_widget && (
                    <div className="my-3 rounded-2xl overflow-hidden border border-[#2c2c2e] bg-black p-2 flex justify-center">
                      <IosBaitFrame config={post.bait_widget} compact />
                    </div>
                  )}

                  <div className="mt-3 flex items-center justify-between gap-2 flex-wrap pt-1 select-none">
                    <div className="flex items-center gap-4 text-[#F3F5F7] -ml-1">
                      <button onClick={() => toggleLike(post.post_id)} className={`flex items-center gap-1.5 transition ${isLiked ? 'text-[#FF3040]' : 'hover:text-[#FF3040]'}`}>
                        <HeartIcon isLiked={isLiked} />
                        <span className={`text-[12px] font-medium ${isLiked ? 'text-[#FF3040]' : 'text-[#777777]'}`}>{likesCount}</span>
                      </button>
                      <button type="button" disabled title="Vista previa: responder no está conectado a Threads" aria-label="Responder (vista previa, no conectado)" className="flex items-center gap-1.5 opacity-70 cursor-not-allowed">
                        <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8}><path strokeLinecap="round" strokeLinejoin="round" d="M12 20.25c4.97 0 9-3.694 9-8.25s-4.03-8.25-9-8.25S3 7.444 3 12c0 2.104.859 4.023 2.273 5.48.332.342.48.82.38 1.285l-.57 2.658 2.87-1.147a1.8 1.8 0 011.08-.09c.92.17 1.93.264 2.967.264z" /></svg>
                        <span className="text-[12px] text-[#777777] font-medium">{post.simulated_replies}</span>
                      </button>
                      <button type="button" disabled title="Vista previa: repostear no está conectado a Threads" aria-label="Repostear (vista previa, no conectado)" className="flex items-center gap-1.5 opacity-70 cursor-not-allowed">
                        <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8}><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 12c0 3.314-2.686 6-6 6H4.5m0 0l3-3m-3 3l3 3M4.5 12c0-3.314 2.686-6 6-6h9m0 0l-3-3m3 3l-3 3" /></svg>
                        <span className="text-[12px] text-[#777777] font-medium">{post.simulated_reposts}</span>
                      </button>
                      <button type="button" disabled title="Vista previa: compartir no está conectado a Threads" aria-label="Compartir (vista previa, no conectado)" className="opacity-70 cursor-not-allowed">
                        <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8}><path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.27 3.13A59.77 59.77 0 0121.48 12 59.77 59.77 0 013.27 20.88L6 12zm0 0h7.5" /></svg>
                      </button>
                    </div>

                    <div className="flex items-center gap-1.5 text-xs">
                      <button type="button" onClick={() => onMutateHook(post.post_id)} className="px-2.5 py-1 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[11px] font-medium transition flex items-center gap-1" title="Genera una variante de plantilla en el backend. No es IA generativa.">
                        <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2L3 14h7v8l11-12h-8z" /></svg>
                        <span>Variante</span>
                      </button>
                      <button type="button" onClick={() => copy(post.post_id, `${post.hook_pattern}\n\n${post.body_slides.join('\n\n')}`)} className="px-2.5 py-1 rounded-lg bg-[#242424] hover:bg-[#2c2c2c] text-zinc-200 border border-[#383838] text-[11px] transition">
                        {copiedId === post.post_id ? 'Copiado' : 'Copiar Post'}
                      </button>
                      <button type="button" onClick={() => onToggleStatus(post.post_id)} title="Seguimiento local: no publica en Threads" className={`px-2.5 py-1 rounded-lg text-[11px] font-medium border transition flex items-center gap-1.5 ${post.status === 'published' ? 'bg-emerald-950/60 border-emerald-500/50 text-emerald-300' : 'bg-zinc-900 border-zinc-800 text-zinc-500 hover:text-zinc-300'}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${post.status === 'published' ? 'bg-emerald-400' : 'bg-zinc-500'}`} aria-hidden="true" />
                        {post.status === 'published' ? 'Marcado publicado (local)' : 'En Cola'}
                      </button>
                    </div>
                  </div>

                  {/* Classic Threads Engagement Cluster Line with Honest Simulation Label */}
                  <div className="mt-2.5 flex items-center justify-between text-[11px] text-[#777777] flex-wrap gap-1">
                    <div className="flex items-center gap-2">
                      <div className="flex -space-x-1.5 overflow-hidden">
                        <img className="inline-block h-4 w-4 rounded-full ring-1 ring-[#181818] object-cover" src="/generated_images/ron_avatar_profile.png" alt="ron" />
                        <img className="inline-block h-4 w-4 rounded-full ring-1 ring-[#181818] object-cover" src="/generated_images/ron_phone_in_hand.png" alt="ron_phone" />
                        <img className="inline-block h-4 w-4 rounded-full ring-1 ring-[#181818] object-cover" src="/generated_images/ron_tired.png" alt="ron2" />
                      </div>
                      <span>{post.simulated_replies} respuestas • {likesCount} Me gusta</span>
                    </div>
                    <span className="text-[9px] font-mono-tech px-1.5 py-0.5 rounded bg-white/[0.04] text-zinc-500 border border-white/[0.06]">
                      VISTA PREVIA — cifras de ejemplo
                    </span>
                  </div>

                  {post.suggested_self_replies?.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-[#262626] space-y-2">
                      <div className="text-[10px] font-mono uppercase tracking-wider text-[#777777]">Auto-Respuestas 1a Hora (Ancla de Conversion)</div>
                      {post.suggested_self_replies.map((reply, rIdx) => {
                        const rKey = `${post.post_id}-rep-${rIdx}`;
                        return (
                          <div key={rIdx} className="bg-[#121212] border border-[#2a2a2a] rounded-xl p-2.5 text-xs flex justify-between items-start gap-2.5">
                            <div className="text-zinc-300 leading-relaxed min-w-0">
                              <span className="text-[#0095F6] text-[11px] font-medium block">@ronoverthinks • #{rIdx + 1}</span>
                              <p className="mt-0.5 text-[13px] text-zinc-200 whitespace-pre-line">{reply}</p>
                            </div>
                            <button onClick={() => copy(rKey, reply)} className="shrink-0 px-2 py-0.5 text-[11px] rounded bg-[#242424] hover:bg-[#2c2c2c] text-zinc-300 border border-zinc-700 transition">
                              {copiedId === rKey ? 'Copiado' : 'Copiar'}
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </div>
  );
};
