import React from 'react';

interface State {
  error: Error | null;
}

interface Props {
  children: React.ReactNode;
}

/** Evita que un error de render deje la app en pantalla blanca. */
export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    console.error('Error de render en Ronin OS:', error, info.componentStack);
  }

  private reset = (): void => {
    this.setState({ error: null });
  };

  render(): React.ReactNode {
    if (!this.state.error) return this.props.children;
    return (
      <div className="min-h-[60vh] flex items-center justify-center p-6 font-ui">
        <div className="max-w-lg w-full bg-[#0e1017] border border-rose-500/40 rounded-2xl p-5 space-y-3">
          <h2 className="text-sm font-bold text-rose-300 font-grotesque">Esta vista no pudo renderizar</h2>
          <p className="text-xs text-zinc-300 leading-relaxed">
            Se produjo un error en el cliente. El resto de la aplicación sigue disponible; cambia de pestaña o reintenta.
          </p>
          <pre className="text-[10px] text-rose-200 bg-black/60 border border-white/10 rounded-lg p-2.5 overflow-x-auto whitespace-pre-wrap break-words">
            {this.state.error.message}
          </pre>
          <button
            type="button"
            onClick={this.reset}
            className="px-3 py-1.5 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/40 text-rose-200 text-[11px] font-mono-tech font-bold transition"
          >
            Reintentar render
          </button>
        </div>
      </div>
    );
  }
}
