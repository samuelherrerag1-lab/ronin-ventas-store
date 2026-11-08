import React, { useMemo, useState } from 'react';
import type { SkillCustomizationItem } from '../../types/domain';
import { CloseIcon, SearchIcon, cx } from './HubBits';
import { categoryLabel } from './connectorMeta';

interface HubSkillsTableProps {
  skills: SkillCustomizationItem[];
  onToggleSkill: (skillId: string, enabled: boolean) => Promise<unknown> | void;
  busyId: string | null;
}

export const HubSkillsTable: React.FC<HubSkillsTableProps> = ({ skills, onToggleSkill, busyId }) => {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');

  const categories = useMemo(() => Array.from(new Set(skills.map((skill) => skill.category))), [skills]);
  const activeCount = skills.filter((skill) => skill.enabled).length;

  const query = search.trim().toLowerCase();
  const filtered = skills.filter((skill) => {
    if (category !== 'all' && skill.category !== category) return false;
    if (!query) return true;
    return (
      skill.name.toLowerCase().includes(query) ||
      skill.skill_id.toLowerCase().includes(query) ||
      categoryLabel(skill.category).toLowerCase().includes(query)
    );
  });

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full sm:w-72">
          <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
          <input
            type="text"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Buscar skill"
            aria-label="Buscar skill"
            className="h-9 w-full rounded-lg border border-white/[0.08] bg-[#0c0d10] pl-9 pr-9 text-[12px] text-zinc-100 outline-none transition-colors duration-150 placeholder:text-zinc-400 focus:border-white/20"
          />
          {search && (
            <button
              type="button"
              onClick={() => setSearch('')}
              aria-label="Limpiar búsqueda"
              className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded p-0.5 text-zinc-400 transition-colors duration-150 hover:text-zinc-100"
            >
              <CloseIcon />
            </button>
          )}
        </div>

        <p className="text-[11px] text-zinc-400">
          <span className="font-mono-tech tabular-nums text-zinc-300">{filtered.length}</span> de {skills.length}
          <span className="mx-1.5 text-zinc-700">·</span>
          <span className="font-mono-tech tabular-nums text-emerald-400/90">{activeCount}</span> activas
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-1">
        {['all', ...categories].map((item) => {
          const active = category === item;
          return (
            <button
              key={item}
              type="button"
              onClick={() => setCategory(item)}
              aria-pressed={active}
              className={cx(
                'h-7 rounded-full px-2.5 text-[11px] transition-colors duration-150 ease-out',
                active
                  ? 'bg-white/[0.09] text-white'
                  : 'text-zinc-400 hover:bg-white/[0.04] hover:text-zinc-200',
              )}
            >
              {item === 'all' ? 'Todas' : categoryLabel(item)}
            </button>
          );
        })}
      </div>

      <div className="overflow-hidden rounded-2xl border border-white/[0.07] bg-[#0d0e11]">
        <div className="max-h-[calc(100vh-300px)] min-h-[320px] overflow-y-auto">
          <table className="w-full table-fixed border-collapse text-left">
            <thead className="sticky top-0 z-10 bg-[#0d0e11]/95 backdrop-blur">
              <tr className="border-b border-white/[0.07] text-[11px] text-zinc-400">
                <th scope="col" className="px-4 py-2.5 font-normal sm:px-5">
                  Skill
                </th>
                <th scope="col" className="hidden w-[160px] px-4 py-2.5 font-normal sm:table-cell">
                  Categoría
                </th>
                <th scope="col" className="w-[72px] px-4 py-2.5 text-right font-normal sm:w-[92px] sm:px-5">
                  Activa
                </th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-5 py-14 text-center">
                    <p className="text-[12px] text-zinc-400">Ninguna skill coincide con “{search}”.</p>
                    <button
                      type="button"
                      onClick={() => {
                        setSearch('');
                        setCategory('all');
                      }}
                      className="mt-2 text-[11px] text-emerald-400 transition-colors duration-150 hover:text-emerald-300"
                    >
                      Limpiar filtros
                    </button>
                  </td>
                </tr>
              ) : (
                filtered.map((skill) => {
                  const busy = busyId === skill.skill_id;
                  return (
                    <tr
                      key={skill.skill_id}
                      className="border-b border-white/[0.04] transition-colors duration-150 last:border-0 hover:bg-white/[0.02]"
                    >
                      <td className="px-4 py-3 sm:px-5">
                        <div
                          title={skill.power_rule}
                          className={cx(
                            'line-clamp-2 text-[13px] leading-snug sm:line-clamp-1',
                            skill.enabled ? 'text-zinc-100' : 'text-zinc-400',
                          )}
                        >
                          {skill.name}
                        </div>
                        <div className="mt-1 flex items-center gap-1.5 text-[11px] leading-none">
                          <span className="truncate font-mono-tech text-zinc-400/80">{skill.skill_id}</span>
                          <span className="shrink-0 text-zinc-700 sm:hidden">·</span>
                          <span className="shrink-0 text-zinc-400 sm:hidden">{categoryLabel(skill.category)}</span>
                        </div>
                      </td>
                      <td className="hidden px-4 py-3 sm:table-cell">
                        <span className="text-[11px] text-zinc-400">{categoryLabel(skill.category)}</span>
                      </td>
                      <td className="px-4 py-3 text-right sm:px-5">
                        <button
                          type="button"
                          role="switch"
                          aria-checked={skill.enabled}
                          aria-label={`${skill.enabled ? 'Desactivar' : 'Activar'} ${skill.name}`}
                          disabled={busy}
                          onClick={() => onToggleSkill(skill.skill_id, skill.enabled)}
                          className="inline-flex h-9 w-10 items-center justify-center rounded-full focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-400/70 disabled:opacity-50"
                        >
                          <span
                            aria-hidden="true"
                            className={cx(
                              'flex h-5 w-[34px] items-center rounded-full transition-colors duration-150 ease-out',
                              skill.enabled ? 'bg-emerald-500' : 'bg-white/[0.14]',
                            )}
                          >
                            <span
                              className={cx(
                                'h-3.5 w-3.5 rounded-full bg-white shadow-sm transition-transform duration-150 ease-out',
                                skill.enabled ? 'translate-x-[17px]' : 'translate-x-[3px]',
                              )}
                            />
                          </span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
