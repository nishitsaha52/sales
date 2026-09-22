import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";

import {
  deactivatePartnerOverride,
  getPartners,
  getPricingConfiguration,
  getProducts,
  getRegistrationOptions,
  getResolvedPricing,
  setPartnerOverride,
  setPartnerTypeRule,
  setTierAdjustment,
  type CommercialTerm,
  type MasterDataItem,
  type TierAdjustment,
} from "../api/client";
import { useAuth } from "../features/auth/AuthContext";

const effectiveFrom = "2026-01-01";

function money(value: string): string {
  return Number(value).toLocaleString(undefined, { style: "currency", currency: "USD" });
}

function TermEditor({ type, term }: { type: MasterDataItem; term?: CommercialTerm }) {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (body: Record<string, unknown>) => setPartnerTypeRule(type.id, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["resolved-pricing"] });
      return queryClient.invalidateQueries({ queryKey: ["pricing-configuration"] });
    },
  });
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    mutation.mutate({ adjustment_type: form.get("adjustment_type"), percentage: form.get("percentage"), effective_from: form.get("effective_from"), effective_until: form.get("effective_until") || null });
  }
  return <form className="rule-row" onSubmit={submit}><strong>{type.name}</strong><select name="adjustment_type" defaultValue={term?.adjustment_type ?? "NONE"}><option value="NONE">No adjustment</option><option value="PERCENT_DISCOUNT">Percent discount</option><option value="PERCENT_MARKUP">Percent markup</option><option value="REFERRAL_COMMISSION">Referral commission</option></select><label><span className="sr-only">Percentage</span><input name="percentage" type="number" step="0.0001" min="0" defaultValue={term?.percentage ?? "0"} /></label><label><span className="sr-only">Effective from</span><input name="effective_from" type="date" defaultValue={term?.effective_from ?? effectiveFrom} /></label><label><span className="sr-only">Effective until</span><input name="effective_until" type="date" defaultValue={term?.effective_until ?? ""} /></label><button className="row-action" type="submit" disabled={mutation.isPending}>Save</button></form>;
}

function TierEditor({ tier, adjustment }: { tier: MasterDataItem; adjustment?: TierAdjustment }) {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (body: Record<string, unknown>) => setTierAdjustment(tier.id, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["resolved-pricing"] });
      return queryClient.invalidateQueries({ queryKey: ["pricing-configuration"] });
    },
  });
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    mutation.mutate({ discount_percentage: form.get("discount_percentage"), effective_from: form.get("effective_from"), effective_until: form.get("effective_until") || null });
  }
  return <form className="rule-row rule-row--tier" onSubmit={submit}><strong>{tier.name}</strong><label><span className="sr-only">Discount percentage</span><input name="discount_percentage" type="number" step="0.0001" min="0" max="100" defaultValue={adjustment?.discount_percentage ?? "0"} /></label><span>% benefit</span><label><span className="sr-only">Effective from</span><input name="effective_from" type="date" defaultValue={adjustment?.effective_from ?? effectiveFrom} /></label><label><span className="sr-only">Effective until</span><input name="effective_until" type="date" defaultValue={adjustment?.effective_until ?? ""} /></label><button className="row-action" type="submit" disabled={mutation.isPending}>Save</button></form>;
}

export function PricingPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const isTcg = Boolean(user?.roles.some((role) => role.startsWith("TCG_")) || user?.is_superuser);
  const isAdmin = Boolean(user?.roles.includes("TCG_ADMIN") || user?.is_superuser);
  const [partnerId, setPartnerId] = useState(user?.partner_id ?? "");
  const [asOf, setAsOf] = useState(() => new Date().toISOString().slice(0, 10));
  const partners = useQuery({ queryKey: ["active-partners"], queryFn: () => getPartners("status=ACTIVE&page_size=100"), enabled: isTcg });
  const options = useQuery({ queryKey: ["registration-options"], queryFn: getRegistrationOptions, enabled: isAdmin });
  const products = useQuery({ queryKey: ["products"], queryFn: getProducts, enabled: isAdmin });
  const configuration = useQuery({ queryKey: ["pricing-configuration"], queryFn: () => getPricingConfiguration(), enabled: isAdmin });
  const pricing = useQuery({ queryKey: ["resolved-pricing", partnerId, asOf], queryFn: () => getResolvedPricing(isTcg ? partnerId : undefined, asOf), enabled: !isTcg || Boolean(partnerId) });
  const overrideMutation = useMutation({
    mutationFn: (body: Record<string, unknown>) => setPartnerOverride(body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["pricing-configuration"] });
      void queryClient.invalidateQueries({ queryKey: ["resolved-pricing"] });
    },
  });
  const deactivateOverride = useMutation({
    mutationFn: deactivatePartnerOverride,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["pricing-configuration"] });
      void queryClient.invalidateQueries({ queryKey: ["resolved-pricing"] });
    },
  });

  function addOverride(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    overrideMutation.mutate({ partner_id: form.get("partner_id"), sku_id: form.get("sku_id"), override_type: form.get("override_type"), value: form.get("value"), effective_from: form.get("effective_from"), effective_until: form.get("effective_until") || null });
  }

  return <div className="workspace-page">
    <header className="page-heading page-heading--row"><div><span className="eyebrow">Commercial pricing</span><h1>{isTcg ? "Partner pricing" : "Your pricing"}</h1><p>Authoritative prices in USD, effective as of the selected date.</p></div><label className="date-filter">As of<input type="date" value={asOf} onChange={(event) => setAsOf(event.target.value)} /></label></header>
    {isTcg && <section className="content-card partner-picker"><label>Partner<select value={partnerId} onChange={(event) => setPartnerId(event.target.value)}><option value="">Select a partner</option>{partners.data?.items.map((partner) => <option value={partner.id} key={partner.id}>{partner.company_name} · {partner.partner_type.name} · {partner.tier?.name ?? "No tier"}</option>)}</select></label></section>}
    {pricing.isLoading && <p className="notice">Resolving pricing…</p>}
    {pricing.data && <section className="content-card table-card pricing-table"><div className="card-heading"><div><span className="status-kicker">{pricing.data.currency}</span><h2>{pricing.data.partner_name}</h2></div><span>{pricing.data.items.length} priced SKUs</span></div>
      {pricing.data.items.length === 0 ? <div className="empty-state"><h2>No effective prices</h2><p>TCG Admin must configure USD list prices for active SKUs.</p></div> : <div className="table-scroll"><table><thead><tr><th>Product / SKU</th>{isAdmin && <th>List price</th>}{isAdmin && <th>Type rule</th>}{isAdmin && <th>Tier</th>}{isAdmin && <th>Override</th>}<th>Final price</th><th>Effective</th></tr></thead><tbody>{pricing.data.items.map((item) => <tr key={item.sku_id}><td><strong>{item.product_name} · {item.sku_name}</strong><small>{item.sku_code} · per {item.unit}</small></td>{isAdmin && <td>{item.breakdown ? money(item.breakdown.list_price) : "—"}</td>}{isAdmin && <td>{item.breakdown?.partner_type_adjustment?.replaceAll("_", " ") ?? "None"}<small>{item.breakdown ? `${item.breakdown.partner_type_percentage}%` : ""}</small></td>}{isAdmin && <td>{item.breakdown?.tier_discount_percentage ?? "0"}%</td>}{isAdmin && <td>{item.breakdown?.override_type?.replaceAll("_", " ") ?? "—"}</td>}<td><strong className="price-value">{money(item.final_price)}</strong>{item.commission_percentage && <small>{item.commission_percentage}% referral commission</small>}</td><td>{item.effective_from}<small>{item.effective_until ? `to ${item.effective_until}` : "No end date"}</small></td></tr>)}</tbody></table></div>}
    </section>}

    {isAdmin && <div className="pricing-config-grid">
      <section className="content-card rule-card"><div className="card-heading"><div><span className="status-kicker">Step 2</span><h2>Partner type rules</h2></div></div>{options.data?.partner_types.map((type) => <TermEditor key={type.id} type={type} term={configuration.data?.commercial_terms.find((term) => term.partner_type_id === type.id && term.is_active)} />)}</section>
      <section className="content-card rule-card"><div className="card-heading"><div><span className="status-kicker">Step 3</span><h2>Tier benefits</h2></div></div>{options.data?.partner_tiers.map((tier) => <TierEditor key={tier.id} tier={tier} adjustment={configuration.data?.tier_adjustments.find((item) => item.tier_id === tier.id && item.is_active)} />)}</section>
      <form className="content-card compact-form override-form" onSubmit={addOverride}><span className="status-kicker">Step 4</span><h2>Partner override</h2><label>Partner<select name="partner_id" required defaultValue=""><option value="" disabled>Select partner</option>{partners.data?.items.map((partner) => <option value={partner.id} key={partner.id}>{partner.company_name}</option>)}</select></label><label>SKU<select name="sku_id" required defaultValue=""><option value="" disabled>Select SKU</option>{products.data?.flatMap((product) => product.skus.map((sku) => <option value={sku.id} key={sku.id}>{product.name} · {sku.name}</option>))}</select></label><label>Override<select name="override_type"><option value="FIXED_PRICE">Fixed USD price</option><option value="PERCENT_DISCOUNT">Percent discount</option><option value="PERCENT_MARKUP">Percent markup</option></select></label><label>Value<input name="value" type="number" min="0" step="0.0001" required /></label><label>Effective from<input name="effective_from" type="date" defaultValue={effectiveFrom} required /></label><label>Effective until<input name="effective_until" type="date" /></label><button type="submit" disabled={overrideMutation.isPending}>Save override</button></form>
      {configuration.data?.partner_overrides.some((override) => override.is_active) && <section className="content-card table-card override-list"><div className="card-heading"><h2>Active overrides</h2></div><div className="table-scroll"><table><thead><tr><th>Partner</th><th>SKU</th><th>Rule</th><th>Value</th><th>Effective</th><th /></tr></thead><tbody>{configuration.data.partner_overrides.filter((override) => override.is_active).map((override) => <tr key={override.id}><td>{override.partner_name}</td><td>{override.sku_code}</td><td>{override.override_type.replaceAll("_", " ")}</td><td>{override.override_type === "FIXED_PRICE" ? money(override.value) : `${override.value}%`}</td><td>{override.effective_from}</td><td><button className="row-action" type="button" onClick={() => deactivateOverride.mutate(override.id)}>Remove</button></td></tr>)}</tbody></table></div></section>}
    </div>}
  </div>;
}
