// ---------------------------------------------------------------------------
// CSRF helper (Django requires the token on POST requests)
// ---------------------------------------------------------------------------
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}
const CSRF_TOKEN = getCookie("csrftoken");

async function postForm(url, data) {
  const body = new URLSearchParams(data);
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": CSRF_TOKEN,
    },
    body,
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(json.error || "Something went wrong.");
  return json;
}

// ---------------------------------------------------------------------------
// Toasts
// ---------------------------------------------------------------------------
function showToast(message, type = "success") {
  const root = document.getElementById("toast-root");
  if (!root) return;
  const toast = document.createElement("div");
  toast.className = `toast ${type === "error" ? "toast-error" : ""}`;
  toast.innerHTML = `<span class="dot"></span><span>${message}</span>`;
  root.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add("show"));
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 2600);
}

// ---------------------------------------------------------------------------
// Cart badge helper
// ---------------------------------------------------------------------------
function setCartBadge(count) {
  document.querySelectorAll("[data-cart-badge]").forEach((el) => {
    el.textContent = count;
    el.style.display = count > 0 ? "inline-flex" : "none";
  });
}

// ---------------------------------------------------------------------------
// Add to cart — works for any button with [data-add-to-cart] + [data-product-id]
// Optional [data-qty-source="#id"] reads quantity from an input/span elsewhere.
// ---------------------------------------------------------------------------
document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-add-to-cart]");
  if (!btn) return;
  e.preventDefault();
  if (btn.disabled) return;

  const productId = btn.dataset.productId;
  let qty = 1;
  if (btn.dataset.qtySource) {
    const src = document.querySelector(btn.dataset.qtySource);
    if (src) qty = parseInt(src.textContent || src.value || "1", 10) || 1;
  }

  const original = btn.innerHTML;
  btn.disabled = true;
  try {
    const data = await postForm("/cart/add/", { product_id: productId, quantity: qty });
    setCartBadge(data.cart_count);
    showToast(data.message || "Added to cart successfully!");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setTimeout(() => {
      btn.disabled = false;
      btn.innerHTML = original;
    }, 250);
  }
});

// ---------------------------------------------------------------------------
// Wishlist toggle — [data-wishlist-toggle] + [data-product-id]
// ---------------------------------------------------------------------------
document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-wishlist-toggle]");
  if (!btn) return;
  e.preventDefault();

  if (btn.dataset.authenticated !== "true") {
    window.location.href = btn.dataset.loginUrl || "/accounts/login/";
    return;
  }

  try {
    const data = await postForm("/wishlist/toggle/", { product_id: btn.dataset.productId });
    btn.classList.toggle("active", data.added);
    btn.textContent = data.added ? "♥" : "♡";
    document.querySelectorAll("[data-wishlist-badge]").forEach((el) => {
      el.textContent = data.wishlist_count;
      el.style.display = data.wishlist_count > 0 ? "inline-flex" : "none";
    });
    showToast(data.added ? "Added to your wishlist" : "Removed from wishlist");
  } catch (err) {
    showToast(err.message, "error");
  }
});

// ---------------------------------------------------------------------------
// Cart page — quantity +/- and remove, updates totals without a reload
// ---------------------------------------------------------------------------
function formatMoney(value) {
  const num = Number(value);
  const formatted = num % 1 === 0 ? num.toLocaleString() : num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  return (window.DUKALINK_CURRENCY || "Rs. ") + formatted;
}

function updateCartSummaryDOM(data) {
  const subtotalEl = document.querySelector("[data-cart-subtotal]");
  const deliveryEl = document.querySelector("[data-cart-delivery]");
  const totalEl = document.querySelector("[data-cart-total]");
  if (subtotalEl) subtotalEl.textContent = formatMoney(data.subtotal);
  if (deliveryEl) deliveryEl.textContent = Number(data.delivery_fee) === 0 ? "Free" : formatMoney(data.delivery_fee);
  if (totalEl) totalEl.textContent = formatMoney(data.total);
  setCartBadge(data.cart_count);
}

document.addEventListener("click", async (e) => {
  const incr = e.target.closest("[data-qty-incr]");
  const decr = e.target.closest("[data-qty-decr]");
  const remove = e.target.closest("[data-cart-remove]");
  if (!incr && !decr && !remove) return;
  e.preventDefault();

  const row = e.target.closest("[data-cart-row]");
  if (!row) return;
  const productId = row.dataset.cartRow;
  const qtyEl = row.querySelector("[data-qty-value]");

  if (remove) {
    const data = await postForm("/cart/remove/", { product_id: productId });
    row.remove();
    updateCartSummaryDOM(data);
    if (data.cart_count === 0) location.reload();
    return;
  }

  let qty = parseInt(qtyEl.textContent, 10);
  qty = incr ? qty + 1 : Math.max(0, qty - 1);

  const data = await postForm("/cart/update/", { product_id: productId, quantity: qty });
  if (data.removed) {
    row.remove();
    if (data.cart_count === 0) {
      location.reload();
      return;
    }
  } else {
    qtyEl.textContent = qty;
    const lineTotalEl = row.querySelector("[data-line-total]");
    if (lineTotalEl) lineTotalEl.textContent = formatMoney(data.line_total);
  }
  updateCartSummaryDOM(data);
});

// ---------------------------------------------------------------------------
// Product detail page quantity selector (client-side only, before add-to-cart)
// ---------------------------------------------------------------------------
document.addEventListener("click", (e) => {
  const plus = e.target.closest("[data-pdp-qty-plus]");
  const minus = e.target.closest("[data-pdp-qty-minus]");
  if (!plus && !minus) return;
  const display = document.getElementById("pdp-qty-value");
  const max = parseInt(display.dataset.max || "99", 10);
  let val = parseInt(display.textContent, 10);
  val = plus ? Math.min(max, val + 1) : Math.max(1, val - 1);
  display.textContent = val;
});

// ---------------------------------------------------------------------------
// Mobile menu toggle
// ---------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("mobile-menu-btn");
  const panel = document.getElementById("mobile-panel");
  if (btn && panel) {
    btn.addEventListener("click", () => panel.classList.toggle("open"));
  }

  // Auto-dismiss server-rendered messages after a few seconds
  document.querySelectorAll(".messages .alert").forEach((el, i) => {
    setTimeout(() => {
      el.style.transition = "opacity 0.3s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 300);
    }, 4000 + i * 300);
  });
});
