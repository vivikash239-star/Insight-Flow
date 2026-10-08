/**
 * InsightFlow Dashboard Client Logic (Tailwind CSS SaaS Edition)
 * Handles interactive product queries, Chart.js visualizations with glowing electric blue & emerald accents,
 * and dynamic insight rendering in Vercel/Stripe style.
 */

let aspectChart = null;

document.addEventListener("DOMContentLoaded", function () {
  initEventListeners();
  // Trigger initial analysis on page load
  runAnalysis();
});

function initEventListeners() {
  const analyzeBtn = document.getElementById("btn-analyze-insights");
  if (analyzeBtn) {
    analyzeBtn.addEventListener("click", function (e) {
      e.preventDefault();
      runAnalysis();
    });
  }

  const productSelect = document.getElementById("select-product-id");
  if (productSelect) {
    productSelect.addEventListener("change", function () {
      runAnalysis();
    });
  }

  const modeSelect = document.getElementById("select-insight-mode");
  if (modeSelect) {
    modeSelect.addEventListener("change", function () {
      runAnalysis();
    });
  }

  // Upload drawer toggle
  const toggleUploadBtn = document.getElementById("btn-toggle-upload");
  const uploadDrawer = document.getElementById("upload-drawer-panel");
  if (toggleUploadBtn && uploadDrawer) {
    toggleUploadBtn.addEventListener("click", function () {
      uploadDrawer.classList.toggle("hidden");
    });
  }

  // Drag & drop dropzone
  const dropzone = document.getElementById("csv-dropzone");
  const fileInput = document.getElementById("file-input-csv");
  if (dropzone && fileInput) {
    dropzone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", function () {
      if (this.files && this.files[0]) {
        const display = document.getElementById("selected-filename-display");
        if (display) display.textContent = "Selected: " + this.files[0].name;
      }
    });

    ["dragenter", "dragover"].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add("border-sky-400", "bg-slate-900/90");
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove("border-sky-400", "bg-slate-900/90");
      });
    });

    dropzone.addEventListener("drop", (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        fileInput.files = e.dataTransfer.files;
        const display = document.getElementById("selected-filename-display");
        if (display) display.textContent = "Selected: " + e.dataTransfer.files[0].name;
      }
    });
  }
}

async function runAnalysis() {
  const productSelect = document.getElementById("select-product-id");
  const modeSelect = document.getElementById("select-insight-mode");
  const dynamicViewContainer = document.getElementById("dynamic-results-content");

  const productId = productSelect ? productSelect.value : "ALL";
  const insightMode = modeSelect ? modeSelect.value : "problem";

  // Loading skeleton in Vercel SaaS style
  if (dynamicViewContainer) {
    dynamicViewContainer.innerHTML = `
      <div class="p-12 text-center text-slate-400">
        <div class="inline-block w-8 h-8 border-2 border-slate-700 border-t-sky-400 rounded-full animate-spin mb-3"></div>
        <p class="text-sm font-medium">Extracting natural-language root causes with PySpark & VADER...</p>
      </div>
    `;
  }

  try {
    const response = await fetch(`/api/insights?product_id=${encodeURIComponent(productId)}&insight_mode=${encodeURIComponent(insightMode)}`);
    const data = await response.json();

    if (data.status === "success") {
      updateSummaryMetrics(data.metrics, data.product);
      updateAspectChart(data.aspect_distribution, insightMode);
      renderActionBanner(data.improvement_suggestion, insightMode);
      renderDynamicResults(data, insightMode);
    } else {
      dynamicViewContainer.innerHTML = `
        <div class="p-8 text-center text-rose-400 bg-slate-850/80 rounded-2xl border border-rose-500/20">
          <i class="fas fa-triangle-exclamation text-2xl mb-2"></i>
          <p class="text-sm">Unable to retrieve product intelligence data.</p>
        </div>
      `;
    }
  } catch (error) {
    console.error("[InsightFlow Client Error]", error);
    if (dynamicViewContainer) {
      dynamicViewContainer.innerHTML = `
        <div class="p-8 text-center text-rose-400 bg-slate-850/80 rounded-2xl border border-rose-500/20">
          <i class="fas fa-plug-circle-xmark text-2xl mb-2"></i>
          <p class="text-sm">Failed to connect to extraction engine.</p>
        </div>
      `;
    }
  }
}

function updateSummaryMetrics(metrics, product) {
  const elTotalReviews = document.getElementById("metric-total-reviews");
  const elFlaggedDefects = document.getElementById("metric-flagged-defects");
  const elFeatureRequests = document.getElementById("metric-feature-requests");
  const elProdTitle = document.getElementById("current-product-name-heading");

  if (elTotalReviews) elTotalReviews.textContent = metrics.total_reviews || 0;
  if (elFlaggedDefects) elFlaggedDefects.textContent = metrics.flagged_defects || 0;
  if (elFeatureRequests) elFeatureRequests.textContent = metrics.feature_requests || 0;
  if (elProdTitle && product) elProdTitle.textContent = `${product.product_name} (${product.product_id})`;
}

function renderActionBanner(suggestion, mode) {
  const bannerContainer = document.getElementById("action-banner-container");
  if (!bannerContainer) return;

  if (mode === "review" && suggestion) {
    bannerContainer.innerHTML = `
      <div class="relative overflow-hidden p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-amber-500/30 shadow-card">
        <div class="absolute top-0 left-0 bottom-0 w-1.5 bg-gradient-to-b from-amber-400 to-amber-600"></div>
        <div class="flex items-start gap-4">
          <div class="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center text-xl flex-shrink-0 border border-amber-500/20 shadow-glow-amber">
            <i class="fas fa-lightbulb"></i>
          </div>
          <div class="flex-1">
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <span class="font-display font-bold text-base text-amber-300">💡 AI Synthesized Action Item</span>
              <span class="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-300 font-semibold border border-amber-500/30">
                <i class="fas fa-crosshairs text-[10px]"></i> Focus: ${escapeHtml(suggestion.focus || "Manufacturing QA")}
              </span>
            </div>
            <p class="text-sm text-slate-200 leading-relaxed">${escapeHtml(suggestion.text)}</p>
          </div>
        </div>
      </div>
    `;
    bannerContainer.classList.remove("hidden");
  } else {
    bannerContainer.innerHTML = "";
    bannerContainer.classList.add("hidden");
  }
}

function updateAspectChart(aspectDistribution, mode) {
  const canvas = document.getElementById("aspectDistributionChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const labels = Object.keys(aspectDistribution || {});
  const values = Object.values(aspectDistribution || {});

  // Create Glowing Gradients (Electric Blue & Emerald Green)
  const electricBlueGradient = ctx.createLinearGradient(0, 0, 0, 240);
  electricBlueGradient.addColorStop(0, "rgba(56, 189, 248, 0.9)");  // Electric Blue Top
  electricBlueGradient.addColorStop(1, "rgba(37, 99, 235, 0.25)");  // Deep Blue Bottom

  const emeraldGlowGradient = ctx.createLinearGradient(0, 0, 0, 240);
  emeraldGlowGradient.addColorStop(0, "rgba(52, 211, 153, 0.9)");  // Emerald Bright Top
  emeraldGlowGradient.addColorStop(1, "rgba(16, 185, 129, 0.25)"); // Emerald Glow Bottom

  const roseGlowGradient = ctx.createLinearGradient(0, 0, 0, 240);
  roseGlowGradient.addColorStop(0, "rgba(244, 63, 94, 0.9)");   // Rose/Red Top
  roseGlowGradient.addColorStop(1, "rgba(225, 29, 72, 0.25)");  // Crimson Bottom

  const purpleGlowGradient = ctx.createLinearGradient(0, 0, 0, 240);
  purpleGlowGradient.addColorStop(0, "rgba(168, 85, 247, 0.9)"); // Purple Top
  purpleGlowGradient.addColorStop(1, "rgba(99, 102, 241, 0.25)"); // Indigo Bottom

  let chartFillColor = electricBlueGradient;
  let chartBorderColor = "#38bdf8";

  if (mode === "problem") {
    chartFillColor = roseGlowGradient;
    chartBorderColor = "#f43f5e";
  } else if (mode === "feature") {
    chartFillColor = purpleGlowGradient;
    chartBorderColor = "#a855f7";
  } else {
    // Review mode: use glowing emerald green
    chartFillColor = emeraldGlowGradient;
    chartBorderColor = "#34d399";
  }

  if (aspectChart) {
    aspectChart.destroy();
  }

  aspectChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels.length ? labels : ["No data"],
      datasets: [
        {
          label: mode === "problem" ? "Defect Frequency" : (mode === "feature" ? "Wishlist Requests" : "Citations"),
          data: values.length ? values : [0],
          backgroundColor: chartFillColor,
          borderColor: chartBorderColor,
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false,
          maxBarThickness: 42,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 750,
        easing: "easeOutQuart",
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: "#1e293b",
          titleColor: "#f8fafc",
          bodyColor: "#94a3b8",
          borderColor: "rgba(255, 255, 255, 0.15)",
          borderWidth: 1,
          padding: 12,
          boxPadding: 6,
          usePointStyle: true,
          titleFont: { family: "'Inter', sans-serif", size: 12, weight: "bold" },
          bodyFont: { family: "'Inter', sans-serif", size: 12 },
        },
      },
      scales: {
        x: {
          grid: {
            display: false,
            drawBorder: false,
          },
          ticks: {
            color: "#94a3b8",
            font: { family: "'Inter', sans-serif", size: 11, weight: "500" },
          },
        },
        y: {
          beginAtZero: true,
          grid: {
            color: "rgba(255, 255, 255, 0.05)",
            drawBorder: false,
          },
          ticks: {
            stepSize: 1,
            color: "#94a3b8",
            font: { family: "'Inter', sans-serif", size: 11 },
          },
        },
      },
    },
  });
}

function renderDynamicResults(data, mode) {
  const container = document.getElementById("dynamic-results-content");
  if (!container) return;

  if (mode === "problem") {
    const defects = data.defects || [];
    if (defects.length === 0) {
      container.innerHTML = `
        <div class="p-12 text-center text-slate-400 bg-slate-850/60 rounded-2xl border border-slate-800">
          <i class="fas fa-circle-check text-emerald-400 text-3xl mb-3"></i>
          <p class="font-medium text-slate-200">Zero Critical Defects Detected</p>
          <p class="text-xs text-slate-500 mt-1">No severe failure sentences flagged in this product partition.</p>
        </div>
      `;
      return;
    }

    let html = `
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-rose-500/10 text-rose-400 flex items-center justify-center text-sm">
            <i class="fas fa-triangle-exclamation"></i>
          </div>
          <div>
            <h3 class="font-display font-semibold text-lg text-white">Critical Defects & Return Drivers</h3>
            <p class="text-xs text-slate-400">Actionable failure points for QA & Manufacturing engineers</p>
          </div>
        </div>
        <span class="text-xs px-3 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 font-semibold">
          ${defects.length} Flagged Sentences
        </span>
      </div>
      <div class="space-y-3">
    `;

    defects.forEach((item) => {
      html += `
        <div class="group relative p-4 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-rose-500/20 hover:border-rose-500/50 shadow-sm hover:shadow-glow-rose transition-all duration-200">
          <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
            <span class="text-xs font-semibold px-2.5 py-0.5 rounded-md bg-rose-500/10 text-rose-300 border border-rose-500/20">
              <i class="fas fa-microchip text-[10px]"></i> ${escapeHtml(item.aspect_tag)}
            </span>
            <div class="flex items-center gap-1.5 text-xs text-rose-400 font-semibold uppercase tracking-wider">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
              </span>
              <span>Failure Point</span>
            </div>
          </div>
          <p class="text-sm text-slate-100 font-medium leading-relaxed">"${escapeHtml(item.sentence_text)}"</p>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;

  } else if (mode === "review") {
    const goodSentences = data.good_sentences || [];
    const badSentences = data.bad_sentences || [];

    let html = `
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-sm">
            <i class="fas fa-comments"></i>
          </div>
          <div>
            <h3 class="font-display font-semibold text-lg text-white">Balanced Feedback & Polarity Split</h3>
            <p class="text-xs text-slate-400">Granular customer sentiment extracted sentence-by-sentence</p>
          </div>
        </div>
        <span class="text-xs px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-semibold">
          ${goodSentences.length + badSentences.length} Total Sentences
        </span>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- Positive Column (Emerald) -->
        <div class="p-5 rounded-2xl bg-slate-800/80 border border-emerald-500/20 shadow-card">
          <div class="flex items-center justify-between pb-3 mb-4 border-b border-emerald-500/20">
            <div class="flex items-center gap-2 font-display font-semibold text-emerald-400 text-sm">
              <i class="fas fa-thumbs-up"></i>
              <span>Customer Praise & Strengths</span>
            </div>
            <span class="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 font-semibold">
              ${goodSentences.length}
            </span>
          </div>
          <div class="space-y-3">
    `;

    if (goodSentences.length === 0) {
      html += `<p class="text-xs text-slate-500 p-4 text-center">No positive feedback sentences found.</p>`;
    } else {
      goodSentences.forEach((item) => {
        html += `
          <div class="p-3.5 rounded-xl bg-slate-900/60 border border-emerald-500/15 hover:border-emerald-500/40 transition-colors">
            <div class="text-[11px] font-semibold text-emerald-400 mb-1.5 flex items-center gap-1.5">
              <i class="fas fa-tag text-[9px]"></i> ${escapeHtml(item.aspect_tag)}
            </div>
            <p class="text-xs text-slate-200 leading-relaxed">"${escapeHtml(item.sentence_text)}"</p>
          </div>
        `;
      });
    }

    html += `
          </div>
        </div>

        <!-- Negative Column (Amber/Rose) -->
        <div class="p-5 rounded-2xl bg-slate-800/80 border border-amber-500/20 shadow-card">
          <div class="flex items-center justify-between pb-3 mb-4 border-b border-amber-500/20">
            <div class="flex items-center gap-2 font-display font-semibold text-amber-400 text-sm">
              <i class="fas fa-thumbs-down"></i>
              <span>Points of Friction & Negative Sentiment</span>
            </div>
            <span class="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-300 font-semibold">
              ${badSentences.length}
            </span>
          </div>
          <div class="space-y-3">
    `;

    if (badSentences.length === 0) {
      html += `<p class="text-xs text-slate-500 p-4 text-center">No negative feedback sentences found.</p>`;
    } else {
      badSentences.forEach((item) => {
        html += `
          <div class="p-3.5 rounded-xl bg-slate-900/60 border border-amber-500/15 hover:border-amber-500/40 transition-colors">
            <div class="text-[11px] font-semibold text-amber-400 mb-1.5 flex items-center gap-1.5">
              <i class="fas fa-triangle-exclamation text-[9px]"></i> ${escapeHtml(item.aspect_tag)}
            </div>
            <p class="text-xs text-slate-200 leading-relaxed">"${escapeHtml(item.sentence_text)}"</p>
          </div>
        `;
      });
    }

    html += `
          </div>
        </div>

      </div>
    `;

    container.innerHTML = html;

  } else if (mode === "feature") {
    const features = data.features || [];
    if (features.length === 0) {
      container.innerHTML = `
        <div class="p-12 text-center text-slate-400 bg-slate-850/60 rounded-2xl border border-slate-800">
          <i class="fas fa-lightbulb text-indigo-400 text-3xl mb-3"></i>
          <p class="font-medium text-slate-200">No Wishlist Demands Extracted</p>
          <p class="text-xs text-slate-500 mt-1">No explicit modal patterns ('wish it had', 'should include') found in this dataset.</p>
        </div>
      `;
      return;
    }

    let html = `
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center text-sm">
            <i class="fas fa-wand-magic-sparkles"></i>
          </div>
          <div>
            <h3 class="font-display font-semibold text-lg text-white">Customer Feature Wishlist & Roadmap</h3>
            <p class="text-xs text-slate-400">Modal pattern matching for upcoming iterations & product backlog</p>
          </div>
        </div>
        <span class="text-xs px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-semibold">
          ${features.length} Roadmap Demands
        </span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    `;

    features.forEach((item) => {
      html += `
        <div class="group relative p-5 rounded-2xl bg-slate-800/80 hover:bg-slate-800 border border-indigo-500/20 hover:border-indigo-500/50 shadow-card hover:shadow-card-hover transition-all duration-300 transform hover:-translate-y-1 flex flex-col justify-between">
          <div class="mb-4">
            <p class="text-xs text-slate-200 leading-relaxed font-medium">"${escapeHtml(item.sentence_text)}"</p>
          </div>
          <div class="flex items-center justify-between pt-3 border-t border-slate-700/60 text-xs">
            <span class="px-2.5 py-0.5 rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-semibold">
              <i class="fas fa-compass text-[10px]"></i> ${escapeHtml(item.aspect_tag)}
            </span>
            <span class="text-[11px] font-semibold text-sky-400 flex items-center gap-1">
              <i class="fas fa-arrow-trend-up"></i> High Demand
            </span>
          </div>
          <div class="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-indigo-500 to-purple-600 opacity-0 group-hover:opacity-100 rounded-b-2xl transition-opacity"></div>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;
  }
}

function escapeHtml(text) {
  if (!text) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
