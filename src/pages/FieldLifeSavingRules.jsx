import React from 'react';
import { FieldShell } from '../components/layout/FieldShell';

export function FieldLifeSavingRules() {
  return (
    <FieldShell activePage="/field-life-saving-rules">
      <main className="mx-auto flex min-h-[calc(100vh-145px)] w-full max-w-[1040px] items-center justify-center px-5 py-8 sm:px-8">
        <section className="w-full max-w-[720px] rounded-2xl border border-[#eadabb] bg-white/90 px-6 py-16 text-center shadow-[0_14px_34px_rgba(61,53,41,0.06)] sm:px-10">
          <h1 className="text-2xl font-black tracking-[-0.03em] text-[#121827]">Life Saving Rules</h1>
          <p className="mt-3 text-sm text-[#66707d]">Rules to be added.</p>
        </section>
      </main>
    </FieldShell>
  );
}
