/**
 * HealthGuard Application Client Core.
 * Coordinates Pharmacy Store, Product Details, Cart, Prescriptions Review,
 * 3D Reminder Triggering, Adherence Dashboard, Order Tracking, and Complete Ecosystem Flow.
 */

const AppState = {
    medicines: [],
    selectedMedicine: null,
    cart: { items: [], subtotal: 0, delivery_fee: 0, total: 0, rx_required: false },
    activePrescriptions: [],
    orders: [],
    reminders: [],
    adherence: { logs: [], adherence_rate: 85.7, current_streak_days: 5 },
    notifications: [],
    consultations: [],
    comparisonList: [],
    currentTab: "store", // store, prescriptions, reminders, consultations, orders, monitoring, ecosystem
    activeFilter: {
        search: "",
        category: "all",
        dosage_form: "all",
        prescription_required: null,
        max_price: 300
    },
    active3DExperience: null,
    zoomActive: false
};

// --- Initialization ---
document.addEventListener("DOMContentLoaded", async () => {
    await loadInitialData();
    setupNavigation();
    setupFilters();
    setupCartEvents();
    renderMedicineGrid();
    renderNotifications();
    setupEcosystemFlow();
});

// --- API Helpers ---
async function apiGet(endpoint) {
    try {
        const res = await fetch(endpoint);
        return await res.json();
    } catch (err) {
        console.error("API GET Error:", endpoint, err);
        return null;
    }
}

async function apiPost(endpoint, body = {}) {
    try {
        const res = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });
        return await res.json();
    } catch (err) {
        console.error("API POST Error:", endpoint, err);
        return null;
    }
}

// --- Data Loading ---
async function loadInitialData() {
    const [medsRes, cartRes, ordersRes, rxRes, remRes, adhRes, notifRes, cnsRes] = await Promise.all([
        apiGet("/api/medicines"),
        apiGet("/api/cart"),
        apiGet("/api/orders"),
        apiGet("/api/prescriptions"),
        apiGet("/api/reminders"),
        apiGet("/api/adherence"),
        apiGet("/api/notifications"),
        apiGet("/api/consultations")
    ]);

    if (medsRes && medsRes.medicines) AppState.medicines = medsRes.medicines;
    if (cartRes) AppState.cart = cartRes;
    if (ordersRes && ordersRes.orders) AppState.orders = ordersRes.orders;
    if (rxRes && rxRes.prescriptions) AppState.activePrescriptions = rxRes.prescriptions;
    if (remRes && remRes.reminders) AppState.reminders = remRes.reminders;
    if (adhRes) AppState.adherence = adhRes;
    if (notifRes && notifRes.notifications) AppState.notifications = notifRes.notifications;
    if (cnsRes && cnsRes.consultations) AppState.consultations = cnsRes.consultations;

    updateCartBadge();
    updateNotificationBadge();
    renderAdherenceDashboard();
    renderOrdersList();
    renderPrescriptionsDesk();
}

// --- Navigation Tabs ---
function setupNavigation() {
    const navButtons = document.querySelectorAll("[data-nav-tab]");
    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-nav-tab");
            switchTab(targetTab);
        });
    });
}

function switchTab(tabName) {
    AppState.currentTab = tabName;
    const views = document.querySelectorAll(".view-section");
    views.forEach(v => v.classList.add("hidden"));

    const targetEl = document.getElementById(`view-${tabName}`);
    if (targetEl) {
        targetEl.classList.remove("hidden");
    }

    // Update active nav styling
    const navButtons = document.querySelectorAll("[data-nav-tab]");
    navButtons.forEach(btn => {
        if (btn.getAttribute("data-nav-tab") === tabName) {
            btn.classList.add("bg-teal-700", "text-white");
            btn.classList.remove("text-teal-100", "hover:bg-teal-600");
        } else {
            btn.classList.remove("bg-teal-700", "text-white");
            btn.classList.add("text-teal-100", "hover:bg-teal-600");
        }
    });

    if (tabName === "reminders") {
        renderAdherenceDashboard();
    } else if (tabName === "orders") {
        renderOrdersList();
    } else if (tabName === "prescriptions") {
        renderPrescriptionsDesk();
    }
}

// --- Search & Filters ---
function setupFilters() {
    const searchInput = document.getElementById("search-input");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            AppState.activeFilter.search = e.target.value.toLowerCase().trim();
            renderMedicineGrid();
        });
    }

    // Dosage Form Pill buttons
    const formPills = document.querySelectorAll("[data-filter-form]");
    formPills.forEach(pill => {
        pill.addEventListener("click", () => {
            formPills.forEach(p => p.classList.remove("active-pill", "bg-teal-600", "text-white"));
            pill.classList.add("active-pill", "bg-teal-600", "text-white");
            AppState.activeFilter.dosage_form = pill.getAttribute("data-filter-form");
            renderMedicineGrid();
        });
    });

    // Prescription Filter Checkbox
    const rxCheck = document.getElementById("filter-rx-req");
    if (rxCheck) {
        rxCheck.addEventListener("change", (e) => {
            if (e.target.value === "all") AppState.activeFilter.prescription_required = null;
            else if (e.target.value === "rx") AppState.activeFilter.prescription_required = true;
            else if (e.target.value === "otc") AppState.activeFilter.prescription_required = false;
            renderMedicineGrid();
        });
    }

    // Price slider
    const priceSlider = document.getElementById("price-slider");
    const priceDisplay = document.getElementById("price-display");
    if (priceSlider && priceDisplay) {
        priceSlider.addEventListener("input", (e) => {
            AppState.activeFilter.max_price = parseFloat(e.target.value);
            priceDisplay.textContent = `₹${AppState.activeFilter.max_price}`;
            renderMedicineGrid();
        });
    }

    // Category Selector
    const catSelect = document.getElementById("filter-category");
    if (catSelect) {
        catSelect.addEventListener("change", (e) => {
            AppState.activeFilter.category = e.target.value;
            renderMedicineGrid();
        });
    }
}

// --- Render Medicine Grid ---
function renderMedicineGrid() {
    const grid = document.getElementById("medicine-grid");
    const countEl = document.getElementById("results-count");
    if (!grid) return;

    let filtered = AppState.medicines.filter(m => {
        // Search
        if (AppState.activeFilter.search) {
            const q = AppState.activeFilter.search;
            const match = (
                m.name.toLowerCase().includes(q) ||
                m.generic_name.toLowerCase().includes(q) ||
                m.brand.toLowerCase().includes(q) ||
                m.manufacturer.toLowerCase().includes(q) ||
                m.category.toLowerCase().includes(q)
            );
            if (!match) return false;
        }

        // Dosage form
        if (AppState.activeFilter.dosage_form !== "all") {
            if (m.dosage_form.toLowerCase() !== AppState.activeFilter.dosage_form.toLowerCase()) {
                return false;
            }
        }

        // Rx
        if (AppState.activeFilter.prescription_required !== null) {
            if (m.prescription_required !== AppState.activeFilter.prescription_required) {
                return false;
            }
        }

        // Category
        if (AppState.activeFilter.category !== "all") {
            if (!m.category.toLowerCase().includes(AppState.activeFilter.category.toLowerCase())) {
                return false;
            }
        }

        // Max price
        if (m.price > AppState.activeFilter.max_price) {
            return false;
        }

        return true;
    });

    if (countEl) {
        countEl.textContent = `${filtered.length} Medicines Available`;
    }

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-16 text-center bg-white rounded-2xl border border-dashed border-slate-300">
                <span class="text-5xl">🔍</span>
                <h3 class="mt-3 text-lg font-bold text-slate-700">No medicines match your filter</h3>
                <p class="text-sm text-slate-500 mt-1">Try resetting search criteria or price limit.</p>
                <button onclick="resetFilters()" class="mt-4 px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-semibold hover:bg-teal-700">
                    Reset Filters
                </button>
            </div>
        `;
        return;
    }

    grid.innerHTML = filtered.map(med => {
        const isCompared = AppState.comparisonList.includes(med.id);
        const rxBadge = med.prescription_required
            ? `<span class="px-2.5 py-1 text-xs font-bold rounded-full bg-amber-100 text-amber-900 border border-amber-300 flex items-center gap-1">
                 <svg class="w-3 h-3 text-amber-700" fill="currentColor" viewBox="0 0 20 20"><path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/><path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/></svg>
                 Rx Required
               </span>`
            : `<span class="px-2.5 py-1 text-xs font-bold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
                 OTC (No Rx)
               </span>`;

        return `
            <div class="medicine-card bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between group">
                <!-- Product Image Area -->
                <div class="relative bg-slate-50 p-4 flex items-center justify-center border-b border-slate-100 h-52 overflow-hidden cursor-pointer" onclick="openMedicineDetails('${med.id}')">
                    <img src="${med.gallery.main}" alt="${med.name}" class="h-44 w-auto object-contain transition-transform duration-500 group-hover:scale-105" />
                    <div class="absolute top-3 left-3">
                        ${rxBadge}
                    </div>
                    <div class="absolute top-3 right-3 flex items-center gap-1.5">
                        <button onclick="event.stopPropagation(); toggleCompare('${med.id}')" title="Compare side by side" class="p-1.5 rounded-lg ${isCompared ? 'bg-indigo-600 text-white' : 'bg-white/90 text-slate-600 hover:bg-white'} border border-slate-200 shadow-sm transition">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                        </button>
                    </div>
                </div>

                <!-- Product Information -->
                <div class="p-5 flex-1 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between text-xs text-slate-500 mb-1">
                            <span class="font-medium text-teal-700 bg-teal-50 px-2 py-0.5 rounded">${med.dosage_form}</span>
                            <span>Pack: ${med.pack_size}</span>
                        </div>
                        <h3 class="text-base font-bold text-slate-900 leading-tight group-hover:text-teal-700 transition cursor-pointer" onclick="openMedicineDetails('${med.id}')">
                            ${med.name}
                        </h3>
                        <p class="text-xs text-slate-500 line-clamp-1 mt-1 font-medium italic">
                            ${med.generic_name}
                        </p>
                        <p class="text-xs text-slate-400 mt-1">
                            Brand: <span class="text-slate-600 font-semibold">${med.brand}</span> • ${med.manufacturer.split(' ')[0]}
                        </p>
                    </div>

                    <!-- Price & Actions -->
                    <div class="mt-4 pt-3 border-t border-slate-100">
                        <div class="flex items-baseline justify-between mb-3">
                            <div class="flex items-baseline gap-2">
                                <span class="text-xl font-extrabold text-slate-900">₹${med.price.toFixed(2)}</span>
                                <span class="text-xs text-slate-400 line-through">₹${med.mrp.toFixed(2)}</span>
                                <span class="text-xs font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">${med.discount_pct}% OFF</span>
                            </div>
                            <span class="text-xs font-semibold ${med.stock_count < 100 ? 'text-amber-600' : 'text-emerald-600'}">
                                ${med.availability}
                            </span>
                        </div>

                        <!-- Buttons: [View Details] [Add to Cart] -->
                        <div class="grid grid-cols-2 gap-2">
                            <button onclick="openMedicineDetails('${med.id}')" class="px-3 py-2 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition text-center">
                                View Details
                            </button>
                            <button onclick="addToCart('${med.id}', 1)" class="px-3 py-2 text-xs font-bold text-white bg-teal-600 hover:bg-teal-700 rounded-xl transition flex items-center justify-center gap-1 shadow-sm hover:shadow">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                                Add Cart
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

function resetFilters() {
    AppState.activeFilter = {
        search: "",
        category: "all",
        dosage_form: "all",
        prescription_required: null,
        max_price: 300
    };
    const searchInput = document.getElementById("search-input");
    if (searchInput) searchInput.value = "";
    const formPills = document.querySelectorAll("[data-filter-form]");
    formPills.forEach(p => {
        p.classList.remove("active-pill", "bg-teal-600", "text-white");
        if (p.getAttribute("data-filter-form") === "all") {
            p.classList.add("active-pill", "bg-teal-600", "text-white");
        }
    });
    renderMedicineGrid();
}

// --- Medicine Details Modal & Gallery ---
function openMedicineDetails(medId) {
    const med = AppState.medicines.find(m => m.id === medId);
    if (!med) return;
    AppState.selectedMedicine = med;

    const modal = document.getElementById("medicine-details-modal");
    if (!modal) return;

    // Fill gallery
    const mainImg = document.getElementById("modal-main-image");
    mainImg.src = med.gallery.main;

    const thumbsContainer = document.getElementById("modal-thumbnails");
    thumbsContainer.innerHTML = `
        <button onclick="switchModalGalleryImage('${med.gallery.main}', this)" class="thumb-btn border-2 border-teal-600 rounded-lg overflow-hidden p-1 bg-white">
            <img src="${med.gallery.main}" class="w-14 h-14 object-contain" alt="Main pack">
        </button>
        <button onclick="switchModalGalleryImage('${med.gallery.packaging}', this)" class="thumb-btn border-2 border-transparent hover:border-slate-300 rounded-lg overflow-hidden p-1 bg-white">
            <img src="${med.gallery.packaging}" class="w-14 h-14 object-contain" alt="Packaging Carton">
        </button>
        <button onclick="switchModalGalleryImage('${med.gallery.dosage_view}', this)" class="thumb-btn border-2 border-transparent hover:border-slate-300 rounded-lg overflow-hidden p-1 bg-white">
            <img src="${med.gallery.dosage_view}" class="w-14 h-14 object-contain" alt="Tablet/Capsule Closeup">
        </button>
        <button onclick="switchModalGalleryImage('${med.gallery.back_view}', this)" class="thumb-btn border-2 border-transparent hover:border-slate-300 rounded-lg overflow-hidden p-1 bg-white">
            <img src="${med.gallery.back_view}" class="w-14 h-14 object-contain" alt="Back & Composition">
        </button>
    `;

    // Fill Details
    document.getElementById("modal-med-name").textContent = med.name;
    document.getElementById("modal-med-generic").textContent = med.generic_name;
    document.getElementById("modal-med-brand").textContent = med.brand;
    document.getElementById("modal-med-mfg").textContent = med.manufacturer;
    document.getElementById("modal-med-pack").textContent = med.pack_size;
    document.getElementById("modal-med-price").textContent = `₹${med.price.toFixed(2)}`;
    document.getElementById("modal-med-mrp").textContent = `₹${med.mrp.toFixed(2)}`;
    document.getElementById("modal-med-discount").textContent = `${med.discount_pct}% OFF`;
    document.getElementById("modal-med-stock").textContent = `${med.availability} (${med.stock_count} units left)`;

    // Prescription Requirement indicator
    const rxTag = document.getElementById("modal-med-rx");
    if (med.prescription_required) {
        rxTag.innerHTML = `
            <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-100 text-amber-900 border border-amber-300 font-bold text-xs rounded-full">
                ⚠️ Prescription Required (Schedule H/H1)
            </span>
        `;
    } else {
        rxTag.innerHTML = `
            <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold text-xs rounded-full">
                ✓ Over-The-Counter (No Prescription Required)
            </span>
        `;
    }

    // Uses, warnings, storage
    document.getElementById("modal-med-uses").textContent = med.uses;
    document.getElementById("modal-med-warnings").textContent = med.warnings;
    document.getElementById("modal-med-storage").textContent = med.storage;
    document.getElementById("modal-med-instructions").textContent = med.dosage_instructions;

    // Side effects tags
    const sideEffectsEl = document.getElementById("modal-med-side-effects");
    if (sideEffectsEl) {
        sideEffectsEl.innerHTML = med.side_effects.map(s => `
            <span class="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs rounded-lg font-medium">${s}</span>
        `).join("");
    }

    modal.classList.remove("hidden");
}

function switchModalGalleryImage(url, btn) {
    const mainImg = document.getElementById("modal-main-image");
    if (mainImg) mainImg.src = url;

    document.querySelectorAll(".thumb-btn").forEach(b => {
        b.classList.remove("border-teal-600");
        b.classList.add("border-transparent");
    });
    if (btn) {
        btn.classList.add("border-teal-600");
        btn.classList.remove("border-transparent");
    }
}

function toggleImageZoom() {
    const img = document.getElementById("modal-main-image");
    if (!img) return;
    AppState.zoomActive = !AppState.zoomActive;
    if (AppState.zoomActive) {
        img.classList.add("scale-150", "cursor-zoom-out");
        img.classList.remove("cursor-zoom-in");
    } else {
        img.classList.remove("scale-150", "cursor-zoom-out");
        img.classList.add("cursor-zoom-in");
    }
}

function closeMedicineDetails() {
    const modal = document.getElementById("medicine-details-modal");
    if (modal) modal.classList.add("hidden");
    AppState.selectedMedicine = null;
    AppState.zoomActive = false;
}

// --- Medicine Comparison Drawer ---
function toggleCompare(medId) {
    const idx = AppState.comparisonList.indexOf(medId);
    if (idx > -1) {
        AppState.comparisonList.splice(idx, 1);
    } else {
        if (AppState.comparisonList.length >= 3) {
            showToast("Comparison limit reached (max 3 medicines).", "warning");
            return;
        }
        AppState.comparisonList.push(medId);
    }
    renderComparisonBar();
    renderMedicineGrid();
}

function renderComparisonBar() {
    const bar = document.getElementById("comparison-bar");
    if (!bar) return;

    if (AppState.comparisonList.length === 0) {
        bar.classList.add("hidden");
        return;
    }

    bar.classList.remove("hidden");
    const countEl = document.getElementById("compare-items-count");
    if (countEl) countEl.textContent = `${AppState.comparisonList.length}/3`;

    const thumbsEl = document.getElementById("compare-thumbs");
    if (thumbsEl) {
        thumbsEl.innerHTML = AppState.comparisonList.map(id => {
            const m = AppState.medicines.find(x => x.id === id);
            return `
                <div class="relative group">
                    <img src="${m.gallery.main}" class="w-10 h-10 object-contain rounded-md bg-white border border-slate-200 p-1" />
                    <button onclick="toggleCompare('${id}')" class="absolute -top-1.5 -right-1.5 bg-rose-500 text-white rounded-full w-4 h-4 text-xs flex items-center justify-center font-bold">×</button>
                </div>
            `;
        }).join("");
    }
}

async function openCompareModal() {
    if (AppState.comparisonList.length === 0) return;
    const res = await apiGet(`/api/compare?ids=${AppState.comparisonList.join(",")}`);
    if (!res || !res.medicines) return;

    const modal = document.getElementById("comparison-modal");
    const content = document.getElementById("comparison-table-content");
    if (!modal || !content) return;

    const meds = res.medicines;

    content.innerHTML = `
        <div class="overflow-x-auto">
            <table class="w-full border-collapse">
                <thead>
                    <tr class="border-b border-slate-200 bg-slate-50">
                        <th class="p-3 text-left text-xs font-bold text-slate-500 uppercase w-48">Parameter</th>
                        ${meds.map(m => `
                            <th class="p-3 text-center min-w-[200px]">
                                <img src="${m.gallery.main}" class="h-24 w-auto object-contain mx-auto mb-2" />
                                <h4 class="font-bold text-slate-900 text-sm">${m.name}</h4>
                                <span class="text-xs text-slate-500">${m.brand}</span>
                            </th>
                        `).join("")}
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-200 text-sm">
                    <tr>
                        <td class="p-3 font-semibold text-slate-600 bg-slate-50">Active Molecule</td>
                        ${meds.map(m => `<td class="p-3 text-center text-slate-700 font-medium">${m.generic_name}</td>`).join("")}
                    </tr>
                    <tr>
                        <td class="p-3 font-semibold text-slate-600 bg-slate-50">Dosage Form</td>
                        ${meds.map(m => `<td class="p-3 text-center"><span class="px-2 py-1 bg-teal-50 text-teal-700 text-xs font-bold rounded">${m.dosage_form}</span></td>`).join("")}
                    </tr>
                    <tr>
                        <td class="p-3 font-semibold text-slate-600 bg-slate-50">Price (Pack Size)</td>
                        ${meds.map(m => `<td class="p-3 text-center font-bold text-slate-900">₹${m.price.toFixed(2)} <span class="text-xs font-normal text-slate-400">(${m.pack_size})</span></td>`).join("")}
                    </tr>
                    <tr>
                        <td class="p-3 font-semibold text-slate-600 bg-slate-50">Prescription Requirement</td>
                        ${meds.map(m => `<td class="p-3 text-center">${m.prescription_required ? '<span class="text-amber-700 font-bold text-xs bg-amber-50 px-2 py-1 rounded">Rx Required</span>' : '<span class="text-emerald-700 font-bold text-xs bg-emerald-50 px-2 py-1 rounded">OTC Direct</span>'}</td>`).join("")}
                    </tr>
                    <tr>
                        <td class="p-3 font-semibold text-slate-600 bg-slate-50">Manufacturer</td>
                        ${meds.map(m => `<td class="p-3 text-center text-xs text-slate-600 font-medium">${m.manufacturer}</td>`).join("")}
                    </tr>
                    <tr>
                        <td class="p-3 font-semibold text-slate-600 bg-slate-50">Primary Indications</td>
                        ${meds.map(m => `<td class="p-3 text-xs text-slate-600 text-left">${m.uses}</td>`).join("")}
                    </tr>
                    <tr>
                        <td class="p-3 font-semibold text-slate-600 bg-slate-50">Storage Condition</td>
                        ${meds.map(m => `<td class="p-3 text-xs text-slate-500 text-center">${m.storage}</td>`).join("")}
                    </tr>
                    <tr>
                        <td class="p-3 font-semibold text-slate-600 bg-slate-50">Action</td>
                        ${meds.map(m => `
                            <td class="p-3 text-center">
                                <button onclick="addToCart('${m.id}', 1)" class="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-bold shadow-sm transition">
                                    Add to Cart
                                </button>
                            </td>
                        `).join("")}
                    </tr>
                </tbody>
            </table>
        </div>
    `;

    modal.classList.remove("hidden");
}

function closeCompareModal() {
    const modal = document.getElementById("comparison-modal");
    if (modal) modal.classList.add("hidden");
}

// --- Cart Operations ---
async function addToCart(medId, quantity = 1) {
    const res = await apiPost("/api/cart/add", { medicine_id: medId, quantity });
    if (res && res.items) {
        AppState.cart = res;
        updateCartBadge();
        renderCartDrawer();
        const med = AppState.medicines.find(m => m.id === medId);
        showToast(`Added ${med ? med.name : 'Medicine'} to cart!`, "success");
    }
}

async function updateCartItemQty(medId, newQty) {
    const res = await apiPost("/api/cart/update", { medicine_id: medId, quantity: newQty });
    if (res && res.items) {
        AppState.cart = res;
        updateCartBadge();
        renderCartDrawer();
    }
}

function updateCartBadge() {
    const badges = document.querySelectorAll(".cart-count-badge");
    const count = AppState.cart.items.reduce((acc, it) => acc + it.quantity, 0);
    badges.forEach(b => {
        b.textContent = count;
        if (count > 0) b.classList.remove("hidden");
        else b.classList.add("hidden");
    });
}

function setupCartEvents() {
    const cartToggle = document.getElementById("cart-toggle-btn");
    const cartClose = document.getElementById("cart-close-btn");
    const cartDrawer = document.getElementById("cart-drawer");

    if (cartToggle && cartDrawer) {
        cartToggle.addEventListener("click", () => {
            renderCartDrawer();
            cartDrawer.classList.remove("translate-x-full");
        });
    }

    if (cartClose && cartDrawer) {
        cartClose.addEventListener("click", () => {
            cartDrawer.classList.add("translate-x-full");
        });
    }
}

function openCartDrawer() {
    const cartDrawer = document.getElementById("cart-drawer");
    if (cartDrawer) {
        renderCartDrawer();
        cartDrawer.classList.remove("translate-x-full");
    }
}

function closeCartDrawer() {
    const cartDrawer = document.getElementById("cart-drawer");
    if (cartDrawer) {
        cartDrawer.classList.add("translate-x-full");
    }
}

function renderCartDrawer() {
    const itemsContainer = document.getElementById("cart-items-container");
    const subtotalEl = document.getElementById("cart-subtotal");
    const deliveryEl = document.getElementById("cart-delivery");
    const discountRow = document.getElementById("cart-discount-row");
    const discountEl = document.getElementById("cart-discount");
    const totalEl = document.getElementById("cart-total");
    const rxNoticeEl = document.getElementById("cart-rx-notice");
    const checkoutBtn = document.getElementById("cart-checkout-btn");

    if (!itemsContainer) return;

    if (AppState.cart.items.length === 0) {
        itemsContainer.innerHTML = `
            <div class="py-16 text-center text-slate-400">
                <span class="text-6xl">🛒</span>
                <p class="mt-4 text-base font-medium text-slate-600">Your Medicine Cart is Empty</p>
                <p class="text-xs text-slate-400 mt-1">Browse our store and add verified healthcare products.</p>
                <button onclick="closeCartDrawer(); switchTab('store');" class="mt-5 px-4 py-2 bg-teal-600 text-white rounded-xl text-xs font-bold hover:bg-teal-700 transition">
                    Explore Medicines
                </button>
            </div>
        `;
        if (subtotalEl) subtotalEl.textContent = "₹0.00";
        if (deliveryEl) deliveryEl.textContent = "₹0.00";
        if (totalEl) totalEl.textContent = "₹0.00";
        if (rxNoticeEl) rxNoticeEl.classList.add("hidden");
        if (checkoutBtn) checkoutBtn.disabled = true;
        return;
    }

    if (checkoutBtn) checkoutBtn.disabled = false;

    // Items List
    itemsContainer.innerHTML = AppState.cart.items.map(it => {
        const med = it.medicine;
        return `
            <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200">
                <img src="${med.gallery.main}" class="w-14 h-14 object-contain rounded-lg bg-white p-1 border border-slate-100" />
                <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-bold text-slate-900 truncate">${med.name}</h4>
                    <span class="text-xs text-slate-400 block">${med.pack_size}</span>
                    <div class="flex items-center gap-2 mt-1">
                        <span class="text-sm font-extrabold text-slate-800">₹${(med.price * it.quantity).toFixed(2)}</span>
                        <span class="text-xs text-slate-400">(₹${med.price.toFixed(2)} / pack)</span>
                    </div>
                </div>
                <!-- Qty +/- -->
                <div class="flex items-center border border-slate-300 rounded-lg bg-white overflow-hidden">
                    <button onclick="updateCartItemQty('${med.id}', ${it.quantity - 1})" class="px-2 py-1 text-slate-600 hover:bg-slate-100 font-bold text-xs">-</button>
                    <span class="px-2 py-1 text-xs font-bold text-slate-800">${it.quantity}</span>
                    <button onclick="updateCartItemQty('${med.id}', ${it.quantity + 1})" class="px-2 py-1 text-slate-600 hover:bg-slate-100 font-bold text-xs">+</button>
                </div>
                <button onclick="updateCartItemQty('${med.id}', 0)" class="text-slate-400 hover:text-rose-500 p-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
            </div>
        `;
    }).join("");

    // Rx required banner
    if (AppState.cart.rx_required) {
        rxNoticeEl.classList.remove("hidden");
    } else {
        rxNoticeEl.classList.add("hidden");
    }

    // Totals
    if (subtotalEl) subtotalEl.textContent = `₹${AppState.cart.subtotal.toFixed(2)}`;
    if (deliveryEl) {
        deliveryEl.textContent = AppState.cart.delivery_fee === 0 ? "FREE" : `₹${AppState.cart.delivery_fee.toFixed(2)}`;
    }
    if (totalEl) totalEl.textContent = `₹${AppState.cart.total.toFixed(2)}`;
}

// --- Coupon Application ---
let currentCoupon = "";
function applyCoupon() {
    const input = document.getElementById("coupon-input");
    if (!input) return;
    const code = input.value.trim().toUpperCase();
    if (!code) return;

    if (["HEALTH20", "FIRSTMED", "FREESHIP"].includes(code)) {
        currentCoupon = code;
        showToast(`Promo Code ${code} applied successfully!`, "success");
        // Recalculate preview
        let disc = 0;
        let del = AppState.cart.delivery_fee;
        if (code === "HEALTH20") disc = AppState.cart.subtotal * 0.20;
        else if (code === "FIRSTMED") disc = Math.min(AppState.cart.subtotal, 100);
        else if (code === "FREESHIP") del = 0;

        const discountRow = document.getElementById("cart-discount-row");
        const discountEl = document.getElementById("cart-discount");
        const totalEl = document.getElementById("cart-total");

        if (discountRow && discountEl) {
            discountRow.classList.remove("hidden");
            discountEl.textContent = `-₹${disc.toFixed(2)}`;
        }
        if (totalEl) {
            totalEl.textContent = `₹${Math.max(0, AppState.cart.subtotal - disc + del).toFixed(2)}`;
        }
    } else {
        showToast("Invalid promo code. Try HEALTH20 or FIRSTMED", "error");
    }
}

// --- Checkout & Prescription Verification Flow ---
function initiateCheckout() {
    if (AppState.cart.items.length === 0) return;

    if (AppState.cart.rx_required) {
        // Must upload or select valid prescription
        closeCartDrawer();
        openPrescriptionVerificationGate();
    } else {
        // OTC order can proceed directly
        closeCartDrawer();
        executeOrderCreation(null);
    }
}

function openPrescriptionVerificationGate() {
    const modal = document.getElementById("rx-verification-modal");
    if (!modal) return;

    // List active approved prescriptions user can choose from
    const selectEl = document.getElementById("rx-existing-selector");
    if (selectEl) {
        selectEl.innerHTML = `
            <option value="">-- Choose from your active HealthGuard Prescriptions --</option>
            ${AppState.activePrescriptions.filter(p => p.status === "Approved").map(p => `
                <option value="${p.prescription_id}">${p.prescription_id} — ${p.doctor_name} (${p.medicine_name})</option>
            `).join("")}
        `;
    }

    modal.classList.remove("hidden");
}

function closePrescriptionVerificationGate() {
    const modal = document.getElementById("rx-verification-modal");
    if (modal) modal.classList.add("hidden");
}

async function submitPrescriptionForOrder() {
    const selectEl = document.getElementById("rx-existing-selector");
    const fileUploadEl = document.getElementById("rx-file-upload");
    const chosenRxId = selectEl ? selectEl.value : "";

    if (!chosenRxId && (!fileUploadEl || !fileUploadEl.files || fileUploadEl.files.length === 0)) {
        showToast("Please select an existing prescription or upload a valid slip.", "warning");
        return;
    }

    let finalRxId = chosenRxId;

    if (!finalRxId && fileUploadEl && fileUploadEl.files[0]) {
        // Upload new prescription
        const file = fileUploadEl.files[0];
        const res = await apiPost("/api/prescriptions/upload", {
            doctor_name: "Dr. External Physician",
            patient_name: "Manik Sharma",
            medicine_id: AppState.cart.items[0].medicine.id,
            medicine_name: AppState.cart.items[0].medicine.name,
            file_name: file.name,
            notes: "Uploaded during cart checkout"
        });
        if (res && res.prescription_id) {
            finalRxId = res.prescription_id;
            AppState.activePrescriptions.unshift(res);
            renderPrescriptionsDesk();
        }
    }

    closePrescriptionVerificationGate();
    await executeOrderCreation(finalRxId);
}

async function executeOrderCreation(prescriptionId) {
    const address = "Flat 402, Green Valley Heights, Sector 14, New Delhi - 110001";
    const res = await apiPost("/api/orders", {
        delivery_address: address,
        prescription_id: prescriptionId,
        coupon_code: currentCoupon
    });

    if (res && res.order_id) {
        AppState.orders.unshift(res);
        AppState.cart = await apiGet("/api/cart");
        updateCartBadge();
        currentCoupon = "";

        // Reload reminders because items were auto-scheduled
        const remRes = await apiGet("/api/reminders");
        if (remRes && remRes.reminders) AppState.reminders = remRes.reminders;

        // Reload notifications
        const notifRes = await apiGet("/api/notifications");
        if (notifRes && notifRes.notifications) AppState.notifications = notifRes.notifications;
        updateNotificationBadge();
        renderNotifications();

        showToast(`Order #${res.order_id} placed successfully!`, "success");
        switchTab("orders");
    } else {
        showToast(res.error || "Failed to place order.", "error");
    }
}

// --- Pharmacist Verification Desk ---
function renderPrescriptionsDesk() {
    const deskContainer = document.getElementById("pharmacist-desk-container");
    if (!deskContainer) return;

    if (AppState.activePrescriptions.length === 0) {
        deskContainer.innerHTML = `<div class="p-8 text-center text-slate-400">No prescriptions found.</div>`;
        return;
    }

    deskContainer.innerHTML = AppState.activePrescriptions.map(rx => {
        const isApproved = rx.status === "Approved";
        const isPending = rx.status === "Pending Review";
        const isRejected = rx.status === "Rejected";

        let statusBadge = isApproved
            ? `<span class="px-3 py-1 bg-emerald-100 text-emerald-800 text-xs font-bold rounded-full">✓ Verified & Approved</span>`
            : (isRejected
                ? `<span class="px-3 py-1 bg-rose-100 text-rose-800 text-xs font-bold rounded-full">✕ Rejected</span>`
                : `<span class="px-3 py-1 bg-amber-100 text-amber-900 text-xs font-bold rounded-full animate-pulse">⏳ Pending Pharmacist Review</span>`);

        return `
            <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-100">
                    <div>
                        <div class="flex items-center gap-2">
                            <h3 class="text-base font-bold text-slate-900">${rx.prescription_id}</h3>
                            ${statusBadge}
                        </div>
                        <p class="text-xs text-slate-500 mt-1">Date: ${rx.date} • Patient: <strong class="text-slate-700">${rx.patient_name}</strong></p>
                    </div>
                    <div class="text-right">
                        <span class="text-xs text-slate-400 block">Prescribing Physician</span>
                        <strong class="text-xs font-bold text-teal-800">${rx.doctor_name}</strong>
                        <span class="text-[11px] text-slate-400 block">Reg: ${rx.doctor_reg || 'MCI-VERIFIED'}</span>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 my-4">
                    <div class="bg-slate-50 p-4 rounded-xl">
                        <span class="text-xs font-bold text-slate-500 uppercase">Prescribed Medicine</span>
                        <h4 class="text-sm font-bold text-slate-900 mt-1">${rx.medicine_name}</h4>
                        <p class="text-xs text-slate-600 mt-1">Dosage: ${rx.dosage}</p>
                        <p class="text-xs text-slate-600">Course Duration: ${rx.duration}</p>
                    </div>
                    <div class="bg-slate-50 p-4 rounded-xl">
                        <span class="text-xs font-bold text-slate-500 uppercase">Pharmacist Verification Record</span>
                        <p class="text-xs text-slate-700 mt-1">Reviewer: <strong>${rx.pharmacist_name || 'Authorized Duty Pharmacist'}</strong></p>
                        <p class="text-xs text-slate-500 italic mt-1">${rx.verification_notes || 'Pending checklist verification.'}</p>
                    </div>
                </div>

                ${isPending ? `
                    <div class="pt-4 border-t border-slate-100 flex items-center justify-between">
                        <span class="text-xs text-amber-700 font-semibold flex items-center gap-1">
                            <span>🛡️</span> Mandatory Clinical Review Gate: Check registration & dosage match
                        </span>
                        <div class="flex items-center gap-2">
                            <button onclick="reviewPrescriptionAction('${rx.prescription_id}', 'reject')" class="px-4 py-2 bg-rose-50 text-rose-700 hover:bg-rose-100 rounded-xl text-xs font-bold transition">
                                Reject Prescription
                            </button>
                            <button onclick="reviewPrescriptionAction('${rx.prescription_id}', 'approve')" class="px-4 py-2 bg-emerald-600 text-white hover:bg-emerald-700 rounded-xl text-xs font-bold transition flex items-center gap-1">
                                ✓ Approve & Authorize Dispense
                            </button>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }).join("");
}

async function reviewPrescriptionAction(rxId, action) {
    const notes = action === "approve"
        ? "Clinically verified against state medical council database. Meets all safety guidelines."
        : "Rejected: Incomplete dosage instructions or mismatched practitioner credentials.";
    const res = await apiPost(`/api/prescriptions/${rxId}/review`, { action, notes });
    if (res && res.prescription_id) {
        const idx = AppState.activePrescriptions.findIndex(p => p.prescription_id === rxId);
        if (idx > -1) AppState.activePrescriptions[idx] = res;
        renderPrescriptionsDesk();

        // Refresh notifications
        const notifRes = await apiGet("/api/notifications");
        if (notifRes && notifRes.notifications) AppState.notifications = notifRes.notifications;
        updateNotificationBadge();
        renderNotifications();

        showToast(`Prescription ${rxId} ${action === 'approve' ? 'Approved' : 'Rejected'}!`, action === 'approve' ? 'success' : 'error');
    }
}

// --- 3D Medicine Reminder Modal & Controls ---
function open3DReminderModal(medicineId, medicineName, scheduledTime, dosageForm) {
    const modal = document.getElementById("reminder-3d-modal");
    if (!modal) return;

    const med = AppState.medicines.find(m => m.id === medicineId) || {
        name: medicineName || "Augmentin 625 Duo Tablet",
        dosage_form: dosageForm || "Tablet",
        dosage_instructions: "Take 1 unit with full glass of water."
    };

    document.getElementById("reminder-modal-med-name").textContent = med.name;
    document.getElementById("reminder-modal-time").textContent = scheduledTime || "08:00 AM";
    document.getElementById("reminder-modal-form").textContent = med.dosage_form;
    document.getElementById("reminder-modal-instructions").textContent = med.dosage_instructions || "Take with water.";

    modal.classList.remove("hidden");

    // Clean up previous 3D canvas if any
    if (AppState.active3DExperience) {
        AppState.active3DExperience.destroy();
    }

    // Initialize Three.js 3D instance
    setTimeout(() => {
        AppState.active3DExperience = new Medicine3DExperience("reminder-3d-canvas-container", {
            dosageForm: med.dosage_form,
            medicineName: med.name,
            autoPlaySequence: true,
            onDoseTaken: () => {
                showToast(`✓ ${med.name} marked as Taken!`, "success");
            }
        });
    }, 100);
}

function close3DReminderModal() {
    const modal = document.getElementById("reminder-3d-modal");
    if (modal) modal.classList.add("hidden");
    if (AppState.active3DExperience) {
        AppState.active3DExperience.destroy();
        AppState.active3DExperience = null;
    }
}

function trigger3DSequenceNow() {
    if (AppState.active3DExperience) {
        AppState.active3DExperience.triggerSwallowingSequence();
    }
}

async function markDoseTaken() {
    const medName = document.getElementById("reminder-modal-med-name").textContent;
    const timeStr = document.getElementById("reminder-modal-time").textContent;

    if (AppState.active3DExperience) {
        AppState.active3DExperience.confirmDoseTaken();
    }

    const res = await apiPost("/api/adherence/record", {
        medicine_name: medName,
        scheduled_time: timeStr,
        status: "Taken",
        prescription_ref: "RX-ACTIVE",
        notes: "Dose verified via 3D Reminder interaction"
    });

    if (res) {
        AppState.adherence = res;
        renderAdherenceDashboard();
    }

    setTimeout(() => {
        close3DReminderModal();
        showToast("✓ Medication Adherence Dashboard updated!", "success");
    }, 1200);
}

async function snoozeDose() {
    const medName = document.getElementById("reminder-modal-med-name").textContent;
    const timeStr = document.getElementById("reminder-modal-time").textContent;

    const res = await apiPost("/api/adherence/record", {
        medicine_name: medName,
        scheduled_time: timeStr,
        status: "Snoozed",
        notes: "Snoozed for 15 minutes by user."
    });

    if (res) {
        AppState.adherence = res;
        renderAdherenceDashboard();
    }

    close3DReminderModal();
    showToast("⏰ Dose snoozed for 15 minutes.", "info");
}

async function skipDosePrompt() {
    const reason = prompt("Please provide a clinical reason for skipping this dose (optional):", "Feeling nauseous / Advised by doctor");
    if (reason === null) return; // user cancelled

    const medName = document.getElementById("reminder-modal-med-name").textContent;
    const timeStr = document.getElementById("reminder-modal-time").textContent;

    const res = await apiPost("/api/adherence/record", {
        medicine_name: medName,
        scheduled_time: timeStr,
        status: "Skipped",
        notes: reason || "Skipped by patient"
    });

    if (res) {
        AppState.adherence = res;
        renderAdherenceDashboard();
    }

    close3DReminderModal();
    showToast("⚠️ Dose skipped and recorded in clinical history.", "warning");
}

// --- Medication Adherence Dashboard ---
function renderAdherenceDashboard() {
    const adh = AppState.adherence;
    if (!adh) return;

    // Metric numbers
    const rateEl = document.getElementById("adherence-rate-num");
    const streakEl = document.getElementById("adherence-streak-num");
    const takenEl = document.getElementById("adherence-taken-num");
    const missedEl = document.getElementById("adherence-missed-num");

    if (rateEl) rateEl.textContent = `${adh.adherence_rate}%`;
    if (streakEl) streakEl.textContent = `${adh.current_streak_days} Days`;
    if (takenEl) takenEl.textContent = adh.taken;
    if (missedEl) missedEl.textContent = adh.missed;

    // Weekly calendar badges
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    days.forEach(day => {
        const badge = document.getElementById(`adh-day-${day.toLowerCase()}`);
        if (badge) {
            const logsForDay = adh.logs.filter(l => l.day === day);
            if (logsForDay.length > 0) {
                const latest = logsForDay[0];
                if (latest.status === "Taken") {
                    badge.innerHTML = `<span class="text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-1 rounded-full border border-emerald-300">✓ Taken</span>`;
                } else if (latest.status === "Missed") {
                    badge.innerHTML = `<span class="text-xs font-bold text-amber-700 bg-amber-100 px-2 py-1 rounded-full border border-amber-300">⚠ Missed</span>`;
                } else {
                    badge.innerHTML = `<span class="text-xs font-bold text-slate-700 bg-slate-100 px-2 py-1 rounded-full">${latest.status}</span>`;
                }
            } else {
                badge.innerHTML = `<span class="text-xs text-slate-400">Scheduled</span>`;
            }
        }
    });

    // History Table
    const tableBody = document.getElementById("adherence-history-tbody");
    if (tableBody) {
        tableBody.innerHTML = adh.logs.map(l => {
            let statusClass = "bg-emerald-100 text-emerald-800";
            if (l.status === "Missed") statusClass = "bg-amber-100 text-amber-900";
            else if (l.status === "Skipped") statusClass = "bg-rose-100 text-rose-800";
            else if (l.status === "Snoozed") statusClass = "bg-blue-100 text-blue-800";

            return `
                <tr class="border-b border-slate-100 hover:bg-slate-50 transition">
                    <td class="py-3 px-4 text-xs font-bold text-slate-900">${l.medicine_name}</td>
                    <td class="py-3 px-4 text-xs text-slate-600">${l.scheduled_time}</td>
                    <td class="py-3 px-4 text-xs text-slate-600">${l.actual_time}</td>
                    <td class="py-3 px-4 text-xs text-slate-500">${l.date} (${l.day})</td>
                    <td class="py-3 px-4">
                        <span class="px-2.5 py-1 text-xs font-bold rounded-full ${statusClass}">
                            ${l.status}
                        </span>
                    </td>
                    <td class="py-3 px-4 text-xs text-slate-400 font-mono">${l.prescription_ref || '--'}</td>
                </tr>
            `;
        }).join("");
    }
}

// --- Order Tracking ---
function renderOrdersList() {
    const container = document.getElementById("orders-list-container");
    if (!container) return;

    if (AppState.orders.length === 0) {
        container.innerHTML = `<div class="p-8 text-center text-slate-400">No orders placed yet.</div>`;
        return;
    }

    const stages = ["Placed", "Confirmed", "Packed", "Shipped", "Delivered"];

    container.innerHTML = AppState.orders.map(ord => {
        return `
            <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm mb-6">
                <!-- Order Header -->
                <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-100">
                    <div>
                        <div class="flex items-center gap-3">
                            <h3 class="text-base font-extrabold text-slate-900">Order #${ord.order_id}</h3>
                            <span class="px-3 py-1 bg-teal-100 text-teal-800 text-xs font-bold rounded-full">
                                ${ord.status}
                            </span>
                        </div>
                        <p class="text-xs text-slate-500 mt-1">Placed on ${ord.order_date} • Courier: <strong>${ord.courier}</strong></p>
                    </div>
                    <div class="text-right">
                        <span class="text-xs text-slate-400 block">Total Amount</span>
                        <span class="text-lg font-black text-slate-900">₹${ord.total.toFixed(2)}</span>
                        <span class="text-[11px] text-emerald-600 block font-semibold">${ord.payment_method}</span>
                    </div>
                </div>

                <!-- 5-Stage Visual Stepper -->
                <div class="my-6 px-2">
                    <div class="relative flex items-center justify-between">
                        <div class="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-slate-200 w-full z-0"></div>
                        <div class="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-teal-600 z-0 transition-all duration-500" style="width: ${(ord.stage_index / (stages.length - 1)) * 100}%"></div>

                        ${stages.map((stage, idx) => {
                            const isCompleted = idx <= ord.stage_index;
                            const isCurrent = idx === ord.stage_index;
                            return `
                                <div class="relative z-10 flex flex-col items-center">
                                    <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-colors duration-300 ${isCompleted ? 'bg-teal-600 text-white' : 'bg-slate-200 text-slate-500'} ${isCurrent ? 'ring-4 ring-teal-100 ring-offset-2' : ''}">
                                        ${isCompleted ? '✓' : idx + 1}
                                    </div>
                                    <span class="text-xs font-bold mt-2 ${isCompleted ? 'text-slate-800' : 'text-slate-400'}">${stage}</span>
                                </div>
                            `;
                        }).join("")}
                    </div>
                </div>

                <!-- Purchased Medicines Item List -->
                <div class="bg-slate-50 rounded-xl p-4 divide-y divide-slate-200/60 mb-4">
                    ${ord.items.map(it => `
                        <div class="py-2 first:pt-0 last:pb-0 flex items-center justify-between gap-4">
                            <div class="flex items-center gap-3">
                                <img src="${it.image}" class="w-12 h-12 object-contain bg-white rounded-lg p-1 border border-slate-200" />
                                <div>
                                    <h4 class="text-sm font-bold text-slate-900">${it.name}</h4>
                                    <span class="text-xs text-slate-500">${it.pack_size}</span>
                                </div>
                            </div>
                            <div class="text-right">
                                <span class="text-sm font-bold text-slate-800">₹${(it.price * it.quantity).toFixed(2)}</span>
                                <span class="text-xs text-slate-400 block">Qty: ${it.quantity}</span>
                            </div>
                        </div>
                    `).join("")}
                </div>

                <!-- Order Controls to simulate live tracking advancement -->
                <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100">
                    <div class="text-xs text-slate-500">
                        <span>Shipping to: <strong>${ord.delivery_address}</strong></span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs font-semibold text-slate-400">Simulate Progress:</span>
                        ${stages.map((s, idx) => `
                            <button onclick="advanceOrderStatus('${ord.order_id}', ${idx})" class="px-2 py-1 text-[11px] font-bold rounded-lg border ${ord.stage_index === idx ? 'bg-teal-600 text-white border-teal-600' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}">
                                ${s}
                            </button>
                        `).join("")}
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

async function advanceOrderStatus(orderId, stageIdx) {
    const res = await apiPost(`/api/orders/${orderId}/status`, { stage_index: stageIdx });
    if (res && res.order_id) {
        const idx = AppState.orders.findIndex(o => o.order_id === orderId);
        if (idx > -1) AppState.orders[idx] = res;
        renderOrdersList();

        // Refresh notifications
        const notifRes = await apiGet("/api/notifications");
        if (notifRes && notifRes.notifications) AppState.notifications = notifRes.notifications;
        updateNotificationBadge();
        renderNotifications();

        showToast(`Order #${orderId} moved to ${res.status}!`, "info");
    }
}

// --- Notifications System ---
function updateNotificationBadge() {
    const badge = document.getElementById("notif-badge");
    const unread = AppState.notifications.filter(n => !n.read).length;
    if (badge) {
        badge.textContent = unread;
        if (unread > 0) badge.classList.remove("hidden");
        else badge.classList.add("hidden");
    }
}

function toggleNotificationsDropdown() {
    const dropdown = document.getElementById("notifications-dropdown");
    if (!dropdown) return;
    dropdown.classList.toggle("hidden");
    renderNotifications();
}

function renderNotifications() {
    const container = document.getElementById("notifications-list");
    if (!container) return;

    if (AppState.notifications.length === 0) {
        container.innerHTML = `<div class="p-6 text-center text-xs text-slate-400">No notifications.</div>`;
        return;
    }

    container.innerHTML = AppState.notifications.map(n => {
        return `
            <div onclick="handleNotificationClick('${n.id}', '${n.action || ''}', '${n.target_medicine_id || ''}', '${n.target_order_id || ''}')" class="p-3.5 border-b border-slate-100 hover:bg-slate-50 transition cursor-pointer flex items-start gap-3 ${n.read ? 'opacity-70' : 'bg-teal-50/40'}">
                <div class="w-2 h-2 rounded-full mt-1.5 ${n.read ? 'bg-transparent' : 'bg-teal-600'}"></div>
                <div class="flex-1">
                    <h5 class="text-xs font-bold text-slate-900">${n.title}</h5>
                    <p class="text-xs text-slate-600 mt-0.5 leading-snug">${n.message}</p>
                    <span class="text-[10px] text-slate-400 mt-1 block">${n.time}</span>
                </div>
            </div>
        `;
    }).join("");
}

async function handleNotificationClick(notifId, action, targetMedId, targetOrderId) {
    await apiPost(`/api/notifications/${notifId}/read`);
    const n = AppState.notifications.find(x => x.id === notifId);
    if (n) n.read = true;
    updateNotificationBadge();
    renderNotifications();

    const dropdown = document.getElementById("notifications-dropdown");
    if (dropdown) dropdown.classList.add("hidden");

    if (action === "open_3d_reminder") {
        open3DReminderModal(targetMedId || "med-aug-625", "Augmentin 625 Duo Tablet", "08:00 AM", "Tablet");
    } else if (action === "view_order") {
        switchTab("orders");
    } else if (action === "view_prescription") {
        switchTab("prescriptions");
    } else if (action === "open_adherence") {
        switchTab("reminders");
    }
}

// --- Complete Ecosystem Interactive Journey Walkthrough ---
function setupEcosystemFlow() {
    // Populate doctor consultations tab
    const cnsContainer = document.getElementById("consultations-list");
    if (!cnsContainer) return;

    cnsContainer.innerHTML = AppState.consultations.map(cns => {
        return `
            <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm mb-6">
                <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-100">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 rounded-xl bg-teal-600 text-white font-bold flex items-center justify-center text-lg">
                            Dr
                        </div>
                        <div>
                            <h3 class="text-base font-bold text-slate-900">${cns.doctor_name}</h3>
                            <span class="text-xs text-teal-700 font-semibold">${cns.specialization}</span>
                            <span class="text-xs text-slate-400 block">${cns.hospital} • Lic #${cns.reg_number}</span>
                        </div>
                    </div>
                    <div class="text-right">
                        <span class="text-xs font-mono font-bold text-slate-500">${cns.consultation_id}</span>
                        <span class="text-xs text-slate-400 block">${cns.date}</span>
                    </div>
                </div>

                <div class="my-4 bg-teal-50/60 p-4 rounded-xl border border-teal-100">
                    <span class="text-xs font-bold text-teal-900 uppercase">Clinical Diagnosis</span>
                    <p class="text-sm font-semibold text-slate-800 mt-1">${cns.diagnosis}</p>
                    <p class="text-xs text-slate-600 mt-1 italic">${cns.clinical_notes}</p>
                </div>

                <div class="mb-4">
                    <h4 class="text-xs font-bold text-slate-500 uppercase mb-2">Prescribed Regimen</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        ${cns.prescriptions.map(rx => `
                            <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
                                <div>
                                    <h5 class="text-xs font-bold text-slate-900">${rx.medicine_name}</h5>
                                    <p class="text-xs text-slate-500">${rx.dosage}</p>
                                    <span class="text-[11px] text-teal-700 font-medium">${rx.food_relation}</span>
                                </div>
                                <span class="text-xs font-bold text-teal-800 bg-teal-100 px-2.5 py-1 rounded-full">${rx.duration}</span>
                            </div>
                        `).join("")}
                    </div>
                </div>

                <div class="pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4">
                    <div class="text-xs text-slate-500">
                        <span>Follow-up: <strong>${cns.follow_up_date}</strong> (${cns.follow_up_notes})</span>
                    </div>
                    <button onclick="orderPrescribedMedicines('${cns.consultation_id}')" class="px-5 py-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-sm">
                        <span>🛒</span> Order Prescribed Medicines
                    </button>
                </div>
            </div>
        `;
    }).join("");
}

async function orderPrescribedMedicines(consultationId) {
    const cns = AppState.consultations.find(c => c.consultation_id === consultationId);
    if (!cns) return;

    for (const rx of cns.prescriptions) {
        await apiPost("/api/cart/add", { medicine_id: rx.medicine_id, quantity: 1 });
    }

    AppState.cart = await apiGet("/api/cart");
    updateCartBadge();
    openCartDrawer();
    showToast(`Added ${cns.prescriptions.length} prescribed medicines to cart!`, "success");
}

// --- Toast Notifications ---
function showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.className = "fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    let bg = "bg-slate-900 text-white";
    if (type === "success") bg = "bg-emerald-600 text-white";
    else if (type === "error") bg = "bg-rose-600 text-white";
    else if (type === "warning") bg = "bg-amber-600 text-white";

    toast.className = `${bg} px-4 py-3 rounded-xl shadow-xl text-xs font-bold flex items-center gap-2 transform transition-all duration-300 translate-y-4 opacity-0 pointer-events-auto`;
    toast.innerHTML = `<span>${type === 'success' ? '✓' : (type === 'error' ? '✕' : 'ℹ')}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.remove("translate-y-4", "opacity-0");
    }, 10);

    setTimeout(() => {
        toast.classList.add("opacity-0", "translate-y-4");
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}
