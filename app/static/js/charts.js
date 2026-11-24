// Chart.js visualizations initialization & dynamic API data loader

document.addEventListener("DOMContentLoaded", function () {
  // Common Chart.js font and layout defaults
  if (typeof Chart !== "undefined") {
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
    Chart.defaults.color = "#64748b";
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
  }

  // 1. Monthly Income vs Expenses Bar Chart
  const cashflowCtx = document.getElementById("monthlyCashflowChart");
  if (cashflowCtx) {
    fetch("/api/charts/monthly-cashflow")
      .then(response => response.json())
      .then(data => {
        new Chart(cashflowCtx, {
          type: "bar",
          data: {
            labels: data.labels,
            datasets: [
              {
                label: "Income",
                data: data.income,
                backgroundColor: "#10b981",
                borderRadius: 6,
                maxBarThickness: 32
              },
              {
                label: "Expenses",
                data: data.expenses,
                backgroundColor: "#ef4444",
                borderRadius: 6,
                maxBarThickness: 32
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: "top",
                labels: { usePointStyle: true, boxWidth: 8 }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                grid: { color: "#f1f5f9" }
              },
              x: {
                grid: { display: false }
              }
            }
          }
        });
      })
      .catch(err => console.error("Error loading cashflow chart:", err));
  }

  // 2. Expense Categories Doughnut Chart
  const expCatCtx = document.getElementById("expenseCategoryChart");
  if (expCatCtx) {
    fetch("/api/charts/expense-categories")
      .then(response => response.json())
      .then(data => {
        if (!data.data || data.data.length === 0) {
          // Display placeholder text if empty
          expCatCtx.parentElement.innerHTML = "<div class='text-center text-muted py-5'><i class='fa-solid fa-chart-pie fa-2x mb-2'></i><p>No expense data recorded yet for this month.</p></div>";
          return;
        }

        new Chart(expCatCtx, {
          type: "doughnut",
          data: {
            labels: data.labels,
            datasets: [
              {
                data: data.data,
                backgroundColor: data.colors,
                borderWidth: 2,
                borderColor: "#ffffff"
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "68%",
            plugins: {
              legend: {
                position: "bottom",
                labels: { usePointStyle: true, boxWidth: 8, padding: 12 }
              }
            }
          }
        });
      })
      .catch(err => console.error("Error loading expense category chart:", err));
  }

  // 3. Investment Asset Allocation Pie Chart
  const assetCtx = document.getElementById("assetAllocationChart");
  if (assetCtx) {
    fetch("/api/charts/asset-allocation")
      .then(response => response.json())
      .then(data => {
        if (!data.data || data.data.length === 0) {
          assetCtx.parentElement.innerHTML = "<div class='text-center text-muted py-5'><i class='fa-solid fa-coins fa-2x mb-2'></i><p>No investment assets recorded yet.</p></div>";
          return;
        }

        new Chart(assetCtx, {
          type: "pie",
          data: {
            labels: data.labels,
            datasets: [
              {
                data: data.data,
                backgroundColor: data.colors,
                borderWidth: 2,
                borderColor: "#ffffff"
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: "bottom",
                labels: { usePointStyle: true, boxWidth: 8, padding: 12 }
              }
            }
          }
        });
      })
      .catch(err => console.error("Error loading asset allocation chart:", err));
  }

  // 4. Monthly Savings Trend Line Chart
  const savingsCtx = document.getElementById("savingsTrendChart");
  if (savingsCtx) {
    fetch("/api/charts/savings-trend")
      .then(response => response.json())
      .then(data => {
        new Chart(savingsCtx, {
          type: "line",
          data: {
            labels: data.labels,
            datasets: [
              {
                label: "Net Savings",
                data: data.data,
                borderColor: "#2563eb",
                backgroundColor: "rgba(37, 99, 235, 0.08)",
                fill: true,
                tension: 0.35,
                pointBackgroundColor: "#2563eb",
                pointRadius: 4
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false }
            },
            scales: {
              y: {
                grid: { color: "#f1f5f9" }
              },
              x: {
                grid: { display: false }
              }
            }
          }
        });
      })
      .catch(err => console.error("Error loading savings trend chart:", err));
  }

  // 5. Portfolio Profit/Loss Performance Horizontal Bar Chart
  const perfCtx = document.getElementById("portfolioPerformanceChart");
  if (perfCtx) {
    fetch("/api/charts/portfolio-performance")
      .then(response => response.json())
      .then(data => {
        if (!data.labels || data.labels.length === 0) {
          perfCtx.parentElement.innerHTML = "<div class='text-center text-muted py-5'><i class='fa-solid fa-chart-line fa-2x mb-2'></i><p>Add investments to see performance returns.</p></div>";
          return;
        }

        const colors = data.profit_loss.map(val => val >= 0 ? "#10b981" : "#ef4444");

        new Chart(perfCtx, {
          type: "bar",
          data: {
            labels: data.labels,
            datasets: [
              {
                label: "Profit / Loss",
                data: data.profit_loss,
                backgroundColor: colors,
                borderRadius: 4
              }
            ]
          },
          options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false }
            },
            scales: {
              x: {
                grid: { color: "#f1f5f9" }
              },
              y: {
                grid: { display: false }
              }
            }
          }
        });
      })
      .catch(err => console.error("Error loading portfolio performance chart:", err));
  }
});
