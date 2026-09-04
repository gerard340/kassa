/* Kassa POC - frontend. Geen framework, alles in 1 bestand. */
(() => {
  const $ = (id) => document.getElementById(id);
  const fmt = new Intl.NumberFormat("nl-NL", { style: "currency", currency: "EUR" });
  const eur = (c) => fmt.format(c / 100);
  const esc = (s) => String(s).replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));

  let catalog = null;
  const state = {
    view: "categories",   // 'categories' | 'products' | 'search'
    cat: null,            // geselecteerde hoofdcategorie
    sub: null,            // geselecteerde subcategorie (id) of null = alle
    search: "",
    cart: [],             // [{product, qty}]
    ageChecked: false,    // NIX18 al bevestigd voor deze bon
    paying: false,
  };

  // ------------------------------------------------------------------ init
  async function init() {
    catalog = await (await fetch("/api/catalog")).json();
    $("store-name").textContent = catalog.store.name;
    renderCatalog();
    renderCart();
    initClock();
    initScanner();
    initScanSim();
    bindEvents();
  }

  function initClock() {
    const tick = () => {
      $("clock").textContent = new Date().toLocaleString("nl-NL", {
        weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
      });
    };
    tick();
    setInterval(tick, 10000);
  }

  // ------------------------------------------------------------------ catalogus
  function visibleProducts() {
    if (state.view === "search") {
      const q = state.search.toLowerCase();
      return catalog.products.filter((p) => p.name.toLowerCase().includes(q) || p.ean.includes(q));
    }
    let list = catalog.products.filter((p) => p.top_category_id === state.cat.id);
    if (state.sub) list = list.filter((p) => p.category_id === state.sub);
    return list;
  }

  function renderCatalog() {
    const grid = $("grid");
    const isCats = state.view === "categories";
    $("btn-back").hidden = isCats;
    $("breadcrumb").hidden = isCats;
    $("subcats").hidden = true;
    grid.classList.toggle("categories", isCats);

    if (isCats) {
      grid.innerHTML = catalog.categories.map((c) => {
        const n = catalog.products.filter((p) => p.top_category_id === c.id).length;
        return `<button class="tile cat" data-cat="${c.id}" style="background:${c.color}">
                  <span class="count">${n} artikelen</span>
                  <span class="icon">${c.icon || ""}</span>
                  <span class="name">${esc(c.name)}</span>
                </button>`;
      }).join("");
      return;
    }

    if (state.view === "products") {
      $("breadcrumb").textContent = state.cat.name;
      if (state.cat.subcategories.length) {
        $("subcats").hidden = false;
        $("subcats").innerHTML =
          `<button class="chip ${state.sub === null ? "active" : ""}" data-sub="">Alles</button>` +
          state.cat.subcategories.map((s) =>
            `<button class="chip ${state.sub === s.id ? "active" : ""}" data-sub="${s.id}">${esc(s.name)}</button>`).join("");
      }
    } else {
      $("breadcrumb").textContent = `Zoeken: "${state.search}"`;
    }

    const list = visibleProducts();
    grid.innerHTML = list.length
      ? list.map(productTile).join("")
      : `<div class="empty">Geen producten gevonden.</div>`;
  }

  function productTile(p) {
    const tags = [];
    if (p.age_restricted) tags.push(`<span class="tag age">18+</span>`);
    if (p.statiegeld_cents) tags.push(`<span class="tag stg">+ ${eur(p.statiegeld_cents)} statiegeld</span>`);
    if (p.stock <= p.min_stock) tags.push(`<span class="tag low">voorraad ${p.stock}</span>`);
    return `<button class="tile prod" data-prod="${p.id}">
              <img src="${p.image_url}" alt="">
              <div class="body">
                <div class="name">${esc(p.name)}</div>
                <div class="price">${eur(p.price_cents)}</div>
                <div class="meta">${tags.join("")}${tags.length ? "" : "per " + esc(p.unit)}</div>
              </div>
            </button>`;
  }

  // ------------------------------------------------------------------ winkelwagen
  function addToCart(product, qty = 1) {
    if (product.age_restricted && !state.ageChecked) {
      showAgeCheck(() => { state.ageChecked = true; addToCart(product, qty); });
      return;
    }
    const line = state.cart.find((l) => l.product.id === product.id);
    if (line) line.qty += qty; else state.cart.push({ product, qty });
    if (product.stock - cartQty(product.id) < 0) toast(`Let op: voorraad van ${product.name} is op`, true);
    renderCart();
  }

  function cartQty(productId) {
    const l = state.cart.find((x) => x.product.id === productId);
    return l ? l.qty : 0;
  }

  function changeQty(productId, delta) {
    const i = state.cart.findIndex((l) => l.product.id === productId);
    if (i < 0) return;
    state.cart[i].qty += delta;
    if (state.cart[i].qty <= 0) state.cart.splice(i, 1);
    renderCart();
  }

  function clearCart() {
    state.cart = [];
    state.ageChecked = false;
    renderCart();
  }

  function totals() {
    let goods = 0, statiegeld = 0;
    const perRate = {};
    for (const l of state.cart) {
      const g = l.qty * l.product.price_cents;
      goods += g;
      statiegeld += l.qty * l.product.statiegeld_cents;
      perRate[l.product.btw_pct] = (perRate[l.product.btw_pct] || 0) + g;
    }
    const btw = Object.keys(perRate).map(Number).sort((a, b) => a - b).map((pct) => {
      const gross = perRate[pct];
      const net = Math.round(gross / (1 + pct / 100));
      return { pct, gross, net, btw: gross - net };
    });
    return { goods, statiegeld, total: goods + statiegeld, btw };
  }

  function renderCart() {
    const box = $("cart-lines");
    const count = state.cart.reduce((n, l) => n + l.qty, 0);
    $("cart-count").textContent = `${count} ${count === 1 ? "artikel" : "artikelen"}`;

    if (!state.cart.length) {
      box.innerHTML = `<div class="cart-empty">Scan een product of kies een categorie.</div>`;
    } else {
      box.innerHTML = state.cart.map((l) => {
        const p = l.product;
        const lineTotal = l.qty * (p.price_cents + p.statiegeld_cents);
        const sub = [`${l.qty} x ${eur(p.price_cents)}`];
        if (p.statiegeld_cents) sub.push(`+ ${l.qty} x ${eur(p.statiegeld_cents)} statiegeld`);
        return `<div class="line">
                  <div><div class="name">${esc(p.name)}</div><div class="sub">${sub.join(" ")}</div></div>
                  <div class="amount">${eur(lineTotal)}</div>
                  <div class="qty">
                    <button data-qty="-1" data-prod="${p.id}">&minus;</button>
                    <span class="n">${l.qty}</span>
                    <button data-qty="1" data-prod="${p.id}">+</button>
                    <button class="del" data-qty="-999" data-prod="${p.id}">&#10005;</button>
                  </div>
                </div>`;
      }).join("");
      box.scrollTop = box.scrollHeight;
    }

    const t = totals();
    $("t-goods").textContent = eur(t.goods);
    $("row-statiegeld").hidden = !t.statiegeld;
    $("t-statiegeld").textContent = eur(t.statiegeld);
    $("row-btw").innerHTML = t.btw.map((b) => `<div><span>waarvan btw ${b.pct}%</span><span>${eur(b.btw)}</span></div>`).join("");
    $("t-total").textContent = eur(t.total);
    $("pay-amount").textContent = t.total ? eur(t.total) : "";
    $("btn-pay").disabled = !t.total;
    $("btn-clear").disabled = !state.cart.length;
  }

  // ------------------------------------------------------------------ scannen
  async function scan(ean) {
    ean = String(ean).trim();
    if (!ean) return;
    // Eerst lokaal (offline-proof), anders de API (ook producten zonder categorie zijn scanbaar)
    let product = catalog.products.find((p) => p.ean === ean);
    if (!product) {
      const res = await fetch(`/api/products/by-ean/${encodeURIComponent(ean)}`);
      if (!res.ok) { toast(`Onbekende barcode: ${ean}`, true); return; }
      product = await res.json();
    }
    addToCart(product);
    toast(`${product.name} ${eur(product.price_cents)}`);
  }

  function initScanner() {
    // HID-scanner gedraagt zich als toetsenbord: snelle reeks tekens, afgesloten met Enter.
    let buf = "", last = 0;
    document.addEventListener("keydown", (e) => {
      if (e.target.matches("input, textarea, select")) return;
      if (state.paying) return;
      const now = Date.now();
      if (now - last > 400) buf = "";
      last = now;
      if (e.key === "Enter") {
        if (buf.length >= 6) scan(buf);
        buf = "";
        return;
      }
      if (/^[0-9A-Za-z]$/.test(e.key)) buf += e.key;
    });
  }

  function initScanSim() {
    const sel = $("sim-select");
    sel.innerHTML = `<option value="">Kies een product&hellip;</option>` +
      catalog.products.map((p) => `<option value="${p.ean}">${esc(p.name)} - ${p.ean}</option>`).join("") +
      `<option value="8712345000622">Cadeaubon 10 euro (geen categorie) - 8712345000622</option>` +
      `<option value="4006381333931">Onbekend product - 4006381333931</option>`;
    sel.addEventListener("change", () => { $("sim-ean").value = sel.value; });
    const doScan = () => { scan($("sim-ean").value); $("sim-ean").value = ""; sel.value = ""; };
    $("sim-scan").addEventListener("click", doScan);
    $("sim-ean").addEventListener("keydown", (e) => { if (e.key === "Enter") doScan(); });
  }

  // ------------------------------------------------------------------ NIX18
  function showAgeCheck(onYes) {
    $("modal-age").hidden = false;
    $("age-yes").onclick = () => { $("modal-age").hidden = true; onYes(); };
    $("age-no").onclick = () => { $("modal-age").hidden = true; toast("Verkoop geweigerd (NIX18)", true); };
  }

  // ------------------------------------------------------------------ pinbetaling (gesimuleerd)
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  let payCancelled = false;

  async function startPayment() {
    const t = totals();
    if (!t.total || state.paying) return;
    state.paying = true;
    payCancelled = false;

    $("modal-pay").hidden = false;
    $("pay-step-wait").hidden = false;
    $("pay-step-done").hidden = true;
    $("term-amount").textContent = eur(t.total);

    const steps = [
      ["Bedrag verzonden naar terminal", 900],
      ["Bied uw kaart aan", 1800],
      ["Bezig met verwerken", 900],
    ];
    for (const [msg, ms] of steps) {
      $("term-msg").textContent = msg;
      await sleep(ms);
      if (payCancelled) return;
    }

    try {
      const pay = await (await fetch("/api/payments/pin", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount_cents: t.total }),
      })).json();
      if (pay.status !== "approved") throw new Error(pay.error || "Betaling geweigerd");

      const res = await fetch("/api/sales", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lines: state.cart.map((l) => ({ product_id: l.product.id, qty: l.qty })),
          payment: { method: "pin", ref: pay.ref, brand: pay.brand, card_masked: pay.card_masked },
        }),
      });
      if (!res.ok) throw new Error((await res.json()).error || "Opslaan mislukt");
      const receipt = await res.json();

      // Voorraad in de lokale catalogus bijwerken
      for (const l of state.cart) l.product.stock -= l.qty;

      $("receipt").innerHTML = renderReceipt(receipt, pay);
      $("pay-step-wait").hidden = true;
      $("pay-step-done").hidden = false;
    } catch (err) {
      $("modal-pay").hidden = true;
      state.paying = false;
      toast(err.message, true);
    }
  }

  function cancelPayment() {
    payCancelled = true;
    state.paying = false;
    $("modal-pay").hidden = true;
    toast("Betaling geannuleerd", true);
  }

  function finishSale() {
    $("modal-pay").hidden = true;
    state.paying = false;
    clearCart();
    goHome();
  }

  function renderReceipt(r, pay) {
    const W = 40;
    const pad = (l, rr) => l + " ".repeat(Math.max(1, W - l.length - rr.length)) + rr;
    const center = (s) => " ".repeat(Math.max(0, Math.floor((W - s.length) / 2))) + s;
    const out = [];
    out.push(center(r.store.name.toUpperCase()));
    out.push(center(r.store.address));
    out.push(center(`KvK ${r.store.kvk}  BTW ${r.store.btw_nummer}`));
    out.push("-".repeat(W));
    for (const l of r.lines) {
      const desc = l.qty > 1 ? `${l.qty} x ${l.name}` : l.name;
      out.push(pad(desc.slice(0, 30), eur(l.qty * l.unit_price_cents)));
      if (l.statiegeld_cents) out.push(pad(`   statiegeld ${l.qty} x ${eur(l.statiegeld_cents)}`, eur(l.qty * l.statiegeld_cents)));
    }
    out.push("-".repeat(W));
    if (r.statiegeld_cents) {
      out.push(pad("Artikelen", eur(r.goods_cents)));
      out.push(pad("Statiegeld (geen btw)", eur(r.statiegeld_cents)));
    }
    out.push(pad("TOTAAL", eur(r.total_cents)));
    out.push(pad(`Pin ${pay.brand} ${pay.card_masked.slice(-4)}`, eur(r.total_cents)));
    out.push("");
    out.push(pad("BTW   grondslag", "btw"));
    for (const b of r.btw) out.push(pad(`${String(b.pct).padStart(2)}%   ${eur(b.net_cents)}`, eur(b.btw_cents)));
    out.push("-".repeat(W));
    out.push(pad(`Bon ${String(r.sale.id).padStart(6, "0")}`, r.sale.ts));
    out.push(`Terminal ${pay.terminal_id}  ${pay.ref}`);
    out.push("");
    out.push(center("Bedankt voor uw aankoop"));
    return esc(out.join("\n"));
  }

  // ------------------------------------------------------------------ navigatie & events
  function goHome() {
    state.view = "categories"; state.cat = null; state.sub = null; state.search = "";
    $("search").value = "";
    renderCatalog();
  }

  function bindEvents() {
    $("grid").addEventListener("click", (e) => {
      const catBtn = e.target.closest("[data-cat]");
      if (catBtn) {
        state.cat = catalog.categories.find((c) => c.id === +catBtn.dataset.cat);
        state.sub = null; state.view = "products";
        renderCatalog();
        return;
      }
      const prodBtn = e.target.closest("[data-prod]");
      if (prodBtn) {
        const p = catalog.products.find((x) => x.id === +prodBtn.dataset.prod);
        if (p) addToCart(p);
      }
    });

    $("subcats").addEventListener("click", (e) => {
      const chip = e.target.closest("[data-sub]");
      if (!chip) return;
      state.sub = chip.dataset.sub ? +chip.dataset.sub : null;
      renderCatalog();
    });

    $("btn-back").addEventListener("click", goHome);

    $("search").addEventListener("input", (e) => {
      state.search = e.target.value.trim();
      if (state.search.length >= 2) { state.view = "search"; renderCatalog(); }
      else if (state.view === "search") goHome();
    });
    $("search").addEventListener("keydown", (e) => {
      // Enter in het zoekveld met een volledige barcode = scannen
      if (e.key === "Enter" && /^\d{8,14}$/.test(e.target.value.trim())) {
        scan(e.target.value.trim()); e.target.value = ""; goHome();
      }
    });

    $("cart-lines").addEventListener("click", (e) => {
      const b = e.target.closest("[data-qty]");
      if (b) changeQty(+b.dataset.prod, +b.dataset.qty);
    });
    $("btn-clear").addEventListener("click", clearCart);
    $("btn-pay").addEventListener("click", startPayment);
    $("pay-cancel").addEventListener("click", cancelPayment);
    $("btn-new").addEventListener("click", finishSale);
    $("btn-print").addEventListener("click", () => window.print());
  }

  // ------------------------------------------------------------------ toast
  let toastTimer = null;
  function toast(msg, isError = false) {
    const el = $("toast");
    el.textContent = msg;
    el.className = "toast" + (isError ? " error" : "");
    el.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.hidden = true; }, 2200);
  }

  init();
})();
