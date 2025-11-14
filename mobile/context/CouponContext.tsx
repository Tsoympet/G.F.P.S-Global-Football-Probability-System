import React, { createContext, useContext, useMemo, useState } from "react";

export type CouponSelection = {
  fixture_id: string;
  league: string;
  league_id: string;
  home: string;
  away: string;
  market: string;
  outcome: string;
  odds: number;
  prob?: number;
};

type CouponContextType = {
  selections: CouponSelection[];
  addSelection: (sel: CouponSelection) => void;
  removeSelection: (index: number) => void;
  clear: () => void;
  totalOdds: number;
};

const CouponContext = createContext<CouponContextType | undefined>(undefined);

export const CouponProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const [selections, setSelections] = useState<CouponSelection[]>([]);

  const addSelection = (sel: CouponSelection) => {
    setSelections(prev => [...prev, sel]);
  };

  const removeSelection = (index: number) => {
    setSelections(prev => prev.filter((_, i) => i !== index));
  };

  const clear = () => setSelections([]);

  const totalOdds = useMemo(
    () => selections.reduce((acc, s) => acc * s.odds, 1),
    [selections]
  );

  return (
    <CouponContext.Provider
      value={{ selections, addSelection, removeSelection, clear, totalOdds }}
    >
      {children}
    </CouponContext.Provider>
  );
};

export const useCoupon = () => {
  const ctx = useContext(CouponContext);
  if (!ctx) throw new Error("useCoupon must be used within CouponProvider");
  return ctx;
};
