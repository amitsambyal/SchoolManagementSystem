document.addEventListener("DOMContentLoaded", function () {
  const table = document.querySelector(".change-list #result_list");
  if (!table) return;

  const headers = Array.from(table.querySelectorAll("thead th")).map(th =>
    th.textContent.trim()
  );

  const rows = table.querySelectorAll("tbody tr");
  rows.forEach(row => {
    const cells = row.querySelectorAll("td");
    cells.forEach((td, index) => {
      if (headers[index]) {
        td.setAttribute("data-label", headers[index]);
      }
    });
  });
});
