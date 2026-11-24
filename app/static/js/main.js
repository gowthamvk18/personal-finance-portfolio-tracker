// Main application JavaScript
document.addEventListener("DOMContentLoaded", function () {
  // 1. Sidebar Toggle for Mobile / Tablet
  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebar = document.querySelector(".app-sidebar");

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", function () {
      sidebar.classList.toggle("show");
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener("click", function (event) {
      if (
        window.innerWidth < 992 &&
        sidebar.classList.contains("show") &&
        !sidebar.contains(event.target) &&
        !sidebarToggle.contains(event.target)
      ) {
        sidebar.classList.remove("show");
      }
    });
  }

  // 2. Dynamic Category Populator for Transaction Forms
  const typeSelect = document.getElementById("transaction_type");
  const categorySelect = document.getElementById("category");

  if (typeSelect && categorySelect) {
    const incomeCategories = [
      "Salary",
      "Freelancing",
      "Business",
      "Interest",
      "Investments",
      "Rental Income",
      "Other"
    ];

    const expenseCategories = [
      "Food",
      "Rent",
      "Transport",
      "Shopping",
      "Healthcare",
      "Education",
      "Bills",
      "Entertainment",
      "Utilities",
      "Insurance",
      "Other"
    ];

    function updateCategoryOptions() {
      const selectedType = typeSelect.value;
      const currentVal = categorySelect.value;
      const list = selectedType === "income" ? incomeCategories : expenseCategories;

      categorySelect.innerHTML = "";
      list.forEach(function (cat) {
        const opt = document.createElement("option");
        opt.value = cat;
        opt.textContent = cat;
        if (cat === currentVal) {
          opt.selected = true;
        }
        categorySelect.appendChild(opt);
      });
    }

    typeSelect.addEventListener("change", updateCategoryOptions);
    // Initialize if categories empty
    if (categorySelect.options.length === 0) {
      updateCategoryOptions();
    }
  }

  // 3. Auto dismiss alert messages after 5 seconds
  const alerts = document.querySelectorAll(".alert.alert-dismissible");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      try {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } catch (e) {}
    }, 5000);
  });
});
