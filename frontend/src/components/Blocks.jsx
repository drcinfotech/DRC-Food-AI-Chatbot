import {
  Star, Clock, MapPin, Utensils, Leaf, Flame, AlertTriangle, ShieldCheck,
  Info, ShoppingCart, CheckCircle2, Circle, Tag, Sparkles, Home, Briefcase,
  Phone, Bike, Receipt, Plus, Minus, Trash2, Soup, Cookie, Coffee, Pizza,
  Salad, IceCream, BadgePercent, ChefHat,
} from "lucide-react";

const ACCENT = "#FB923C";

const fmtINR = (n) => "₹" + Math.abs(Number(n)).toLocaleString("en-IN", { maximumFractionDigits: 0 });

const SPICE_META = {
  none:   { label: "No spice",  color: "rgba(255,255,255,0.4)" },
  mild:   { label: "Mild",      color: "#86efac" },
  medium: { label: "Medium",    color: "#fde047" },
  hot:    { label: "Hot",       color: "#fca5a5" },
};

const ALLERGEN_LABELS = {
  nuts: "Nuts", gluten: "Gluten", dairy: "Dairy", egg: "Egg",
  shellfish: "Shellfish", fish: "Fish", soy: "Soy", sesame: "Sesame",
};

/* ─── TextBlock ────────────────────────────────────────── */
export function TextBlock({ content }) {
  const parts = content.split(/(\*\*[^*]+\*\*)/g);
  return (
    <div
      className="text-sm leading-relaxed px-4 py-2.5 rounded-2xl rounded-tl-md"
      style={{ background: "rgba(255,255,255,0.03)", color: "rgba(255,255,255,0.88)" }}
    >
      {parts.map((p, i) =>
        p.startsWith("**") && p.endsWith("**") ? (
          <strong key={i} className="text-white font-medium">{p.slice(2, -2)}</strong>
        ) : (
          <span key={i}>{p.split("\n").map((line, j, arr) => (
            <span key={j}>{line}{j < arr.length - 1 && <br />}</span>
          ))}</span>
        )
      )}
    </div>
  );
}

/* ─── DisclaimerBlock ──────────────────────────────────── */
export function DisclaimerBlock({ content }) {
  return (
    <div
      className="flex items-start gap-2.5 px-4 py-2.5 rounded-2xl border"
      style={{ background: "rgba(250, 204, 21, 0.04)", borderColor: "rgba(250, 204, 21, 0.18)", color: "rgba(250, 204, 21, 0.85)" }}
    >
      <Info size={14} className="mt-0.5 flex-shrink-0" />
      <div className="text-11 leading-relaxed">{content}</div>
    </div>
  );
}

/* ─── AllergenAlertBlock (allergen / payment / social-eng) ─── */
export function AllergenAlertBlock({ headline, message, indicators, offer }) {
  return (
    <div
      className="rounded-2xl border-2 p-4 allergen-pulse"
      style={{
        background: "linear-gradient(180deg, rgba(251,146,60,0.10), rgba(251,146,60,0.02))",
        borderColor: "rgba(251,146,60,0.4)",
      }}
    >
      <div className="flex items-center gap-2 mb-2">
        <ShieldCheck size={18} style={{ color: ACCENT }} />
        <div className="text-sm font-semibold" style={{ color: ACCENT }}>{headline}</div>
      </div>
      <div className="text-xs leading-relaxed mb-3" style={{ color: "rgba(255,255,255,0.85)" }}>{message}</div>
      <div className="space-y-1 mb-3">
        {indicators.map((it, i) => (
          <div key={i} className="flex items-start gap-2 text-11" style={{ color: "rgba(255,255,255,0.7)" }}>
            <AlertTriangle size={10} style={{ color: ACCENT, marginTop: 3, flexShrink: 0 }} />
            <span>{it}</span>
          </div>
        ))}
      </div>
      <div
        className="flex items-start gap-2 px-3 py-2 rounded-lg border"
        style={{ background: "rgba(255,255,255,0.04)", borderColor: ACCENT + "33" }}
      >
        <Sparkles size={12} style={{ color: ACCENT, marginTop: 2, flexShrink: 0 }} />
        <div className="text-11 leading-relaxed" style={{ color: "rgba(255,255,255,0.9)" }}>{offer}</div>
      </div>
    </div>
  );
}

/* ─── Restaurant card helper ───────────────────────────── */
function RestaurantCard({ r }) {
  return (
    <div className="rounded-xl p-3 border"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="flex items-start gap-3">
        <div className="rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ width: 44, height: 44, background: ACCENT + "14" }}>
          {r.veg_only
            ? <Leaf size={18} style={{ color: "#86efac" }} />
            : <Utensils size={18} style={{ color: ACCENT }} />}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-0.5">
            <div className="text-xs font-medium" style={{ color: "white" }}>{r.name}</div>
            <span className="text-9 px-1.5 py-0.5 rounded-full font-medium flex items-center gap-1 flex-shrink-0"
              style={{ background: r.rating >= 4.5 ? "rgba(134,239,172,0.15)" : "rgba(251,146,60,0.15)",
                       color: r.rating >= 4.5 ? "#86efac" : ACCENT }}>
              <Star size={9} fill="currentColor" /> {r.rating}
            </span>
          </div>
          <div className="text-10 mb-1.5" style={{ color: "rgba(255,255,255,0.55)" }}>
            {r.tagline}
          </div>
          <div className="flex items-center justify-between gap-2 text-10" style={{ color: "rgba(255,255,255,0.6)" }}>
            <span className="flex items-center gap-1"><MapPin size={9} /> {r.area}</span>
            <span className="flex items-center gap-1"><Clock size={9} /> {r.delivery_minutes} min</span>
            <span className="flex items-center gap-1">
              <span className="font-mono">{fmtINR(r.price_for_two)}</span>
              <span style={{ color: "rgba(255,255,255,0.4)" }}>for two</span>
            </span>
            {r.open_now ? (
              <span className="text-9 px-1.5 py-0.5 rounded-full" style={{ background: "rgba(134,239,172,0.15)", color: "#86efac" }}>OPEN</span>
            ) : (
              <span className="text-9 px-1.5 py-0.5 rounded-full" style={{ background: "rgba(252,165,165,0.15)", color: "#fca5a5" }}>CLOSED</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── RestaurantListBlock ──────────────────────────────── */
export function RestaurantListBlock({ title, items, total }) {
  return (
    <div className="space-y-2">
      {title && (
        <div className="flex items-center justify-between px-1">
          <div className="text-10 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.4)" }}>{title}</div>
          <div className="text-10 font-mono" style={{ color: "rgba(255,255,255,0.55)" }}>{total} restaurants</div>
        </div>
      )}
      {items.map((r) => <RestaurantCard key={r.id} r={r} />)}
    </div>
  );
}

/* ─── RestaurantDetailBlock ────────────────────────────── */
export function RestaurantDetailBlock({ restaurant: r }) {
  return (
    <div className="rounded-xl border overflow-hidden"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="px-4 py-3 border-b" style={{ borderColor: "rgba(255,255,255,0.06)", background: ACCENT + "0C" }}>
        <div className="flex items-center justify-between mb-1">
          <div className="text-sm font-medium" style={{ color: "white" }}>{r.name}</div>
          <span className="text-9 px-1.5 py-0.5 rounded-full font-medium flex items-center gap-1"
            style={{ background: r.rating >= 4.5 ? "rgba(134,239,172,0.15)" : "rgba(251,146,60,0.15)",
                     color: r.rating >= 4.5 ? "#86efac" : ACCENT }}>
            <Star size={9} fill="currentColor" /> {r.rating} ({r.review_count})
          </span>
        </div>
        <div className="text-11" style={{ color: "rgba(255,255,255,0.65)" }}>{r.tagline}</div>
      </div>
      <div className="px-4 py-3 grid grid-cols-3 gap-3 border-b" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
        <div>
          <div className="text-9 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.4)" }}>Delivery</div>
          <div className="text-xs flex items-center gap-1" style={{ color: "white" }}><Clock size={11} /> {r.delivery_minutes} min</div>
          <div className="text-10 font-mono" style={{ color: "rgba(255,255,255,0.5)" }}>{r.distance_km} km away</div>
        </div>
        <div>
          <div className="text-9 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.4)" }}>Cost for two</div>
          <div className="text-xs font-mono" style={{ color: ACCENT }}>{fmtINR(r.price_for_two)}</div>
        </div>
        <div>
          <div className="text-9 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.4)" }}>Area</div>
          <div className="text-xs flex items-center gap-1" style={{ color: "white" }}><MapPin size={11} /> {r.area}</div>
        </div>
      </div>
      <div className="px-4 py-3">
        <div className="text-10 uppercase tracking-tightest2 mb-1.5" style={{ color: "rgba(255,255,255,0.4)" }}>Cuisine</div>
        <div className="flex flex-wrap gap-1">
          {r.cuisine.map((c, i) => (
            <span key={i} className="text-10 px-2 py-0.5 rounded-full" style={{ background: ACCENT + "1A", color: ACCENT }}>{c}</span>
          ))}
          {r.veg_only && (
            <span className="text-10 px-2 py-0.5 rounded-full flex items-center gap-1"
              style={{ background: "rgba(134,239,172,0.15)", color: "#86efac" }}>
              <Leaf size={9} /> Veg only
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

/* ─── Dish card ────────────────────────────────────────── */
function DishRow({ item, showWarning = false }) {
  const spice = SPICE_META[item.spice] || SPICE_META.none;
  return (
    <div className="flex items-start gap-3 px-3 py-2.5 rounded-md"
      style={{ background: showWarning ? "rgba(251,146,60,0.06)" : "rgba(255,255,255,0.02)" }}>
      <div className="flex-shrink-0 rounded-sm mt-1" style={{
        width: 12, height: 12,
        border: `1.5px solid ${item.veg ? "#86efac" : "#fca5a5"}`,
        display: "flex", alignItems: "center", justifyContent: "center"
      }}>
        <div style={{ width: 5, height: 5, borderRadius: "50%", background: item.veg ? "#86efac" : "#fca5a5" }} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <div className="text-xs font-medium" style={{ color: "white" }}>{item.name}</div>
          <div className="text-xs font-mono flex-shrink-0" style={{ color: ACCENT }}>{fmtINR(item.price)}</div>
        </div>
        <div className="text-10 mt-0.5" style={{ color: "rgba(255,255,255,0.55)" }}>{item.description}</div>
        <div className="flex items-center gap-2 mt-1.5 flex-wrap">
          {item.spice && item.spice !== "none" && (
            <span className="text-9 flex items-center gap-0.5" style={{ color: spice.color }}>
              <Flame size={9} /> {spice.label}
            </span>
          )}
          {item.allergens && item.allergens.length > 0 && (
            <span className="text-9" style={{ color: showWarning ? ACCENT : "rgba(255,255,255,0.5)" }}>
              Contains: {item.allergens.map(a => ALLERGEN_LABELS[a] || a).join(", ")}
            </span>
          )}
          {showWarning && (
            <span className="text-9 px-1.5 py-0.5 rounded-full font-medium flex items-center gap-1"
              style={{ background: ACCENT + "22", color: ACCENT }}>
              <AlertTriangle size={9} /> Contains your allergen
            </span>
          )}
          <span className="text-9 font-mono ml-auto" style={{ color: "rgba(255,255,255,0.35)" }}>{item.id}</span>
        </div>
      </div>
    </div>
  );
}

/* ─── MenuBlock ────────────────────────────────────────── */
export function MenuBlock({ restaurant, items, grouped = true }) {
  const groups = grouped
    ? items.reduce((acc, it) => { (acc[it.category] = acc[it.category] || []).push(it); return acc; }, {})
    : { Menu: items };
  return (
    <div className="rounded-xl border overflow-hidden"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="px-4 py-3 border-b flex items-center justify-between"
        style={{ borderColor: "rgba(255,255,255,0.06)", background: ACCENT + "0C" }}>
        <div className="flex items-center gap-2">
          <ChefHat size={14} style={{ color: ACCENT }} />
          <span className="text-xs font-medium" style={{ color: "white" }}>{restaurant.name}</span>
        </div>
        <span className="text-10 font-mono" style={{ color: "rgba(255,255,255,0.55)" }}>{items.length} items</span>
      </div>
      <div className="px-4 py-3 space-y-3">
        {Object.entries(groups).map(([cat, list]) => (
          <div key={cat}>
            <div className="text-10 uppercase tracking-tightest2 mb-1.5" style={{ color: "rgba(255,255,255,0.4)" }}>{cat}</div>
            <div className="space-y-1">
              {list.map((it) => <DishRow key={it.id} item={it} showWarning={it.allergen_warning} />)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── DishCardBlock ────────────────────────────────────── */
export function DishCardBlock({ item, restaurant_name }) {
  return (
    <div className="rounded-xl border overflow-hidden"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="px-4 py-3 border-b text-10 uppercase tracking-tightest2"
        style={{ borderColor: "rgba(255,255,255,0.06)", color: "rgba(255,255,255,0.55)" }}>
        From {restaurant_name}
      </div>
      <div className="p-3">
        <DishRow item={item} />
      </div>
    </div>
  );
}

/* ─── CartBlock ────────────────────────────────────────── */
export function CartBlock({ restaurant_name, items, subtotal, delivery_fee, tax, discount, total, applied_offer, allergen_warnings }) {
  return (
    <div className="rounded-xl border overflow-hidden"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="px-4 py-3 border-b flex items-center justify-between"
        style={{ borderColor: "rgba(255,255,255,0.06)", background: ACCENT + "0C" }}>
        <div className="flex items-center gap-2">
          <ShoppingCart size={14} style={{ color: ACCENT }} />
          <span className="text-xs font-medium" style={{ color: "white" }}>{restaurant_name || "Your cart"}</span>
        </div>
        {applied_offer && (
          <span className="text-9 px-1.5 py-0.5 rounded-full flex items-center gap-1 font-medium"
            style={{ background: ACCENT + "22", color: ACCENT }}>
            <BadgePercent size={9} /> {applied_offer}
          </span>
        )}
      </div>

      <div className="px-4 py-3 border-b" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
        {items.map((line, i) => (
          <div key={i} className="flex items-center justify-between gap-2 py-1.5 text-xs">
            <div className="flex items-center gap-2 flex-1 min-w-0">
              <span className="font-mono text-10 px-1.5 py-0.5 rounded-md"
                style={{ background: "rgba(255,255,255,0.05)", color: "rgba(255,255,255,0.7)" }}>
                {line.qty}×
              </span>
              <span style={{ color: "white" }}>{line.name}</span>
              {line.has_warning && (
                <AlertTriangle size={10} style={{ color: ACCENT, flexShrink: 0 }} />
              )}
            </div>
            <span className="font-mono" style={{ color: "rgba(255,255,255,0.9)" }}>{fmtINR(line.price * line.qty)}</span>
          </div>
        ))}
      </div>

      <div className="px-4 py-3 space-y-1 text-xs">
        <div className="flex justify-between">
          <span style={{ color: "rgba(255,255,255,0.55)" }}>Subtotal</span>
          <span className="font-mono" style={{ color: "rgba(255,255,255,0.9)" }}>{fmtINR(subtotal)}</span>
        </div>
        <div className="flex justify-between">
          <span style={{ color: "rgba(255,255,255,0.55)" }}>Delivery fee</span>
          <span className="font-mono" style={{ color: "rgba(255,255,255,0.9)" }}>{fmtINR(delivery_fee)}</span>
        </div>
        <div className="flex justify-between">
          <span style={{ color: "rgba(255,255,255,0.55)" }}>GST (5%)</span>
          <span className="font-mono" style={{ color: "rgba(255,255,255,0.9)" }}>{fmtINR(tax)}</span>
        </div>
        {discount > 0 && (
          <div className="flex justify-between">
            <span style={{ color: "#86efac" }}>Discount ({applied_offer})</span>
            <span className="font-mono" style={{ color: "#86efac" }}>−{fmtINR(discount)}</span>
          </div>
        )}
        <div className="flex justify-between pt-2 mt-1 border-t" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
          <span className="font-medium" style={{ color: "white" }}>Total</span>
          <span className="font-mono font-medium" style={{ color: ACCENT, fontSize: 14 }}>{fmtINR(total)}</span>
        </div>
      </div>

      {allergen_warnings && allergen_warnings.length > 0 && (
        <div className="px-4 py-2 border-t flex items-start gap-2"
          style={{ borderColor: ACCENT + "33", background: ACCENT + "0F" }}>
          <AlertTriangle size={11} style={{ color: ACCENT, marginTop: 2, flexShrink: 0 }} />
          <div className="text-10" style={{ color: "rgba(255,255,255,0.85)" }}>
            <div style={{ color: ACCENT, fontWeight: 500, marginBottom: 2 }}>Allergen check:</div>
            {allergen_warnings.map((w, i) => <div key={i}>• {w}</div>)}
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── OrderTrackingBlock ───────────────────────────────── */
export function OrderTrackingBlock({ order_id, restaurant_name, status, steps, eta_minutes, rider }) {
  return (
    <div className="rounded-xl border overflow-hidden"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="px-4 py-3 border-b" style={{ borderColor: "rgba(255,255,255,0.06)", background: ACCENT + "0C" }}>
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2">
            <Receipt size={14} style={{ color: ACCENT }} />
            <span className="text-xs font-medium" style={{ color: "white" }}>{restaurant_name}</span>
          </div>
          <span className="text-10 font-mono" style={{ color: "rgba(255,255,255,0.55)" }}>{order_id}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-10 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.55)" }}>{status}</span>
          <span className="text-11 font-mono px-2 py-0.5 rounded-full" style={{ background: ACCENT + "22", color: ACCENT }}>
            ETA {eta_minutes} min
          </span>
        </div>
      </div>

      {/* Vertical timeline */}
      <div className="px-4 py-4">
        {steps.map((step, i) => {
          const last = i === steps.length - 1;
          return (
            <div key={i} className="flex items-start gap-3" style={{ paddingBottom: last ? 0 : 12 }}>
              <div className="relative flex flex-col items-center">
                <div className="rounded-full flex items-center justify-center" style={{
                  width: 18, height: 18,
                  background: step.done ? ACCENT : "rgba(255,255,255,0.08)",
                  color: step.done ? "#0A0A0A" : "rgba(255,255,255,0.4)",
                }}>
                  {step.done ? <CheckCircle2 size={11} /> : <Circle size={9} />}
                </div>
                {!last && (
                  <div style={{
                    position: "absolute", top: 18, bottom: -12, width: 2,
                    background: step.done ? ACCENT : "rgba(255,255,255,0.08)",
                  }} />
                )}
              </div>
              <div className="flex-1 min-w-0 pb-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs" style={{ color: step.done ? "white" : "rgba(255,255,255,0.5)" }}>{step.label}</span>
                  {step.time && (
                    <span className="text-10 font-mono" style={{ color: "rgba(255,255,255,0.45)" }}>{step.time}</span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Rider */}
      {rider && (
        <div className="px-4 py-3 border-t flex items-center justify-between" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
          <div className="flex items-center gap-2">
            <div className="rounded-full flex items-center justify-center" style={{ width: 32, height: 32, background: ACCENT + "14", color: ACCENT }}>
              <Bike size={14} />
            </div>
            <div>
              <div className="text-xs font-medium" style={{ color: "white" }}>{rider.name}</div>
              <div className="text-10" style={{ color: "rgba(255,255,255,0.5)" }}>{rider.vehicle}</div>
            </div>
          </div>
          <button className="text-10 px-2.5 py-1 rounded-full border flex items-center gap-1"
            style={{ borderColor: ACCENT + "44", color: ACCENT, background: "transparent" }}>
            <Phone size={10} /> Call
          </button>
        </div>
      )}
    </div>
  );
}

/* ─── OrderHistoryBlock ────────────────────────────────── */
export function OrderHistoryBlock({ items }) {
  return (
    <div className="space-y-2">
      <div className="text-10 uppercase tracking-tightest2 px-1" style={{ color: "rgba(255,255,255,0.4)" }}>
        Past orders
      </div>
      {items.map((o) => (
        <div key={o.id} className="rounded-xl p-3 border"
          style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
          <div className="flex items-center justify-between gap-2 mb-2">
            <div className="text-xs font-medium" style={{ color: "white" }}>{o.restaurant_name}</div>
            <span className="text-9 px-1.5 py-0.5 rounded-full font-medium"
              style={{ background: "rgba(134,239,172,0.15)", color: "#86efac" }}>{o.status}</span>
          </div>
          <div className="space-y-0.5 mb-2">
            {o.items.map((it, i) => (
              <div key={i} className="text-10" style={{ color: "rgba(255,255,255,0.65)" }}>
                {it.qty}× {it.name}
              </div>
            ))}
          </div>
          <div className="flex items-center justify-between text-10 pt-2 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
            <span style={{ color: "rgba(255,255,255,0.45)" }}>{o.placed_at}</span>
            <div className="flex items-center gap-2">
              {o.rating && (
                <span className="flex items-center gap-0.5" style={{ color: "#fde047" }}>
                  <Star size={9} fill="currentColor" /> {o.rating}
                </span>
              )}
              <span className="font-mono font-medium" style={{ color: ACCENT }}>{fmtINR(o.total)}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── OffersBlock ──────────────────────────────────────── */
export function OffersBlock({ items }) {
  return (
    <div className="space-y-2">
      <div className="text-10 uppercase tracking-tightest2 px-1" style={{ color: "rgba(255,255,255,0.4)" }}>
        Offers for you
      </div>
      {items.map((o) => (
        <div key={o.code} className="rounded-xl p-3 border flex items-start gap-3"
          style={{ background: "rgba(255,255,255,0.03)", borderColor: ACCENT + "22" }}>
          <div className="rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ width: 40, height: 40, background: ACCENT + "14" }}>
            <Tag size={16} style={{ color: ACCENT }} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2 mb-1">
              <div className="text-xs font-medium" style={{ color: "white" }}>{o.headline}</div>
              <span className="text-10 font-mono px-1.5 py-0.5 rounded-md"
                style={{ background: ACCENT + "22", color: ACCENT, letterSpacing: "0.08em" }}>
                {o.code}
              </span>
            </div>
            <div className="text-10" style={{ color: "rgba(255,255,255,0.6)" }}>{o.applicable}</div>
            <div className="flex items-center gap-3 text-10 mt-1" style={{ color: "rgba(255,255,255,0.45)" }}>
              <span>Min order {fmtINR(o.min_order)}</span>
              <span>·</span>
              <span>Expires {o.expires}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── AddressBlock ─────────────────────────────────────── */
export function AddressBlock({ items }) {
  return (
    <div className="space-y-2">
      <div className="text-10 uppercase tracking-tightest2 px-1" style={{ color: "rgba(255,255,255,0.4)" }}>
        Delivery addresses
      </div>
      {items.map((a) => (
        <div key={a.id} className="rounded-xl p-3 border flex items-start gap-3"
          style={{ background: "rgba(255,255,255,0.03)", borderColor: a.is_default ? ACCENT + "33" : "rgba(255,255,255,0.08)" }}>
          <div className="rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ width: 36, height: 36, background: ACCENT + "14" }}>
            {a.label === "Home"  ? <Home      size={15} style={{ color: ACCENT }} /> :
             a.label === "Work"  ? <Briefcase size={15} style={{ color: ACCENT }} /> :
                                   <MapPin    size={15} style={{ color: ACCENT }} />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <div className="text-xs font-medium" style={{ color: "white" }}>{a.label}</div>
              {a.is_default && (
                <span className="text-9 px-1.5 py-0.5 rounded-full font-medium"
                  style={{ background: ACCENT + "22", color: ACCENT }}>DEFAULT</span>
              )}
            </div>
            <div className="text-10" style={{ color: "rgba(255,255,255,0.65)" }}>{a.line1}</div>
            <div className="text-10" style={{ color: "rgba(255,255,255,0.45)" }}>{a.line2}, {a.city} {a.pincode}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── DietaryFilterBlock ───────────────────────────────── */
export function DietaryFilterBlock({ diet, matching_items, note }) {
  return (
    <div className="rounded-xl border overflow-hidden"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="px-4 py-3 border-b flex items-center justify-between"
        style={{ borderColor: "rgba(255,255,255,0.06)", background: ACCENT + "0C" }}>
        <div className="flex items-center gap-2">
          <Leaf size={14} style={{ color: "#86efac" }} />
          <span className="text-xs font-medium" style={{ color: "white" }}>{diet} options</span>
        </div>
        <span className="text-10 font-mono" style={{ color: "rgba(255,255,255,0.55)" }}>{matching_items.length} items</span>
      </div>
      <div className="px-4 py-3 space-y-1">
        {matching_items.map((it) => <DishRow key={it.id} item={it} />)}
      </div>
      {note && (
        <div className="px-4 py-2.5 border-t flex items-start gap-2 text-10"
          style={{ borderColor: "rgba(250, 204, 21, 0.18)", background: "rgba(250, 204, 21, 0.04)", color: "rgba(250, 204, 21, 0.85)" }}>
          <Info size={11} style={{ marginTop: 2, flexShrink: 0 }} />
          <span>{note}</span>
        </div>
      )}
    </div>
  );
}

/* ─── RecommendationBlock ──────────────────────────────── */
export function RecommendationBlock({ rationale, items }) {
  return (
    <div className="rounded-xl border overflow-hidden"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="px-4 py-3 border-b flex items-start gap-2"
        style={{ borderColor: "rgba(255,255,255,0.06)", background: ACCENT + "0C" }}>
        <Sparkles size={14} style={{ color: ACCENT, marginTop: 2, flexShrink: 0 }} />
        <div>
          <div className="text-xs font-medium" style={{ color: "white" }}>Recommended for you</div>
          <div className="text-10 mt-0.5" style={{ color: "rgba(255,255,255,0.55)" }}>{rationale}</div>
        </div>
      </div>
      <div className="px-4 py-3 space-y-1">
        {items.map((it) => <DishRow key={it.id} item={it} />)}
      </div>
    </div>
  );
}

/* ─── Dispatcher ───────────────────────────────────────── */
export default function Block({ block }) {
  switch (block.type) {
    case "text":             return <TextBlock {...block} />;
    case "disclaimer":       return <DisclaimerBlock {...block} />;
    case "allergen_alert":   return <AllergenAlertBlock {...block} />;
    case "restaurant_list":  return <RestaurantListBlock {...block} />;
    case "restaurant_detail":return <RestaurantDetailBlock {...block} />;
    case "menu":             return <MenuBlock {...block} />;
    case "dish_card":        return <DishCardBlock {...block} />;
    case "cart":             return <CartBlock {...block} />;
    case "order_tracking":   return <OrderTrackingBlock {...block} />;
    case "order_history":    return <OrderHistoryBlock {...block} />;
    case "offers":           return <OffersBlock {...block} />;
    case "addresses":        return <AddressBlock {...block} />;
    case "dietary_filter":   return <DietaryFilterBlock {...block} />;
    case "recommendation":   return <RecommendationBlock {...block} />;
    default:
      return (
        <div className="text-xs px-3 py-2 rounded-md" style={{ background: "rgba(255,255,255,0.04)", color: "rgba(255,255,255,0.5)" }}>
          [Unknown block type: {block.type}]
        </div>
      );
  }
}
