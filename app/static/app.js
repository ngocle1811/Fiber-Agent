const elements = {
  filterForm: document.querySelector("#filter-form"),
  resetButton: document.querySelector("#reset-button"),
  pageSize: document.querySelector("#page-size"),
  resultsBody: document.querySelector("#results-body"),
  emptyState: document.querySelector("#empty-state"),
  notice: document.querySelector("#notice"),
  resultDescription: document.querySelector("#result-description"),
  summaryNumber: document.querySelector("#summary-number"),
  summaryLabel: document.querySelector("#summary-label"),
  paginationInfo: document.querySelector("#pagination-info"),
  pageNumber: document.querySelector("#page-number"),
  previousPage: document.querySelector("#previous-page"),
  nextPage: document.querySelector("#next-page"),
  systemState: document.querySelector("#system-state"),
  systemStateText: document.querySelector("#system-state-text"),
  chatForm: document.querySelector("#chat-form"),
  chatMessage: document.querySelector("#chat-message"),
  chatSubmit: document.querySelector("#chat-submit"),
  chatAnswer: document.querySelector("#chat-answer"),
  dialog: document.querySelector("#point-dialog"),
  dialogTitle: document.querySelector("#dialog-title"),
  dialogBody: document.querySelector("#dialog-body"),
  dialogClose: document.querySelector("#dialog-close"),
  dialogDone: document.querySelector("#dialog-done"),
  mapLink: document.querySelector("#map-link"),
};

const state = {
  filters: {},
  exactCode: "",
  limit: Number(elements.pageSize.value),
  offset: 0,
  total: 0,
  requestId: 0,
};

const numberFormatter = new Intl.NumberFormat("vi-VN");

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error("Máy chủ trả về dữ liệu không hợp lệ.");
  }

  if (!response.ok || payload.success === false) {
    throw new Error(payload.error?.message || `Yêu cầu thất bại (${response.status}).`);
  }

  return payload;
}

async function checkSystem() {
  try {
    const health = await apiRequest("/api/health");
    const connected = health.database === "connected";
    elements.systemState.className = `system-state ${connected ? "connected" : "error"}`;
    elements.systemStateText.textContent = connected
      ? "Dữ liệu đang kết nối"
      : "Mất kết nối dữ liệu";
  } catch {
    elements.systemState.className = "system-state error";
    elements.systemStateText.textContent = "Không thể kiểm tra hệ thống";
  }
}

function readFilters() {
  const formData = new FormData(elements.filterForm);
  const values = Object.fromEntries(formData.entries());
  state.exactCode = String(values.ma_diem || "").trim().toUpperCase();
  delete values.ma_diem;

  state.filters = Object.fromEntries(
    Object.entries(values)
      .map(([key, value]) => [key, String(value).trim()])
      .filter(([, value]) => value !== ""),
  );
}

function buildListUrl() {
  const params = new URLSearchParams({
    ...state.filters,
    limit: String(state.limit),
    offset: String(state.offset),
  });
  return `/api/network-points?${params.toString()}`;
}

async function loadPoints() {
  const requestId = ++state.requestId;
  setTableLoading(true);
  hideNotice();

  try {
    let points;

    if (state.exactCode) {
      const payload = await apiRequest(`/api/network-points/${encodeURIComponent(state.exactCode)}`);
      points = [payload.data];
      state.total = 1;
      state.offset = 0;
      elements.resultDescription.textContent = `Kết quả theo mã ${state.exactCode}`;
    } else {
      const payload = await apiRequest(buildListUrl());
      points = payload.data;
      state.total = payload.meta.total ?? points.length;
      const filterCount = Object.keys(state.filters).length;
      elements.resultDescription.textContent = filterCount
        ? `Đang áp dụng ${filterCount} điều kiện lọc`
        : "Tất cả điểm đang hoạt động trong hệ thống";
    }

    if (requestId !== state.requestId) return;
    renderRows(points);
    updateSummary();
    updatePagination(points.length);
  } catch (error) {
    if (requestId !== state.requestId) return;
    state.total = 0;
    renderRows([]);
    updateSummary();
    updatePagination(0);
    showNotice(error.message);
  } finally {
    if (requestId === state.requestId) setTableLoading(false);
  }
}

function setTableLoading(isLoading) {
  elements.previousPage.disabled = isLoading;
  elements.nextPage.disabled = isLoading;

  if (!isLoading) return;
  elements.emptyState.hidden = true;
  elements.resultsBody.replaceChildren();

  for (let rowIndex = 0; rowIndex < 7; rowIndex += 1) {
    const row = document.createElement("tr");
    row.className = "loading-row";
    for (let columnIndex = 0; columnIndex < 7; columnIndex += 1) {
      const cell = document.createElement("td");
      const skeleton = document.createElement("span");
      skeleton.className = "skeleton";
      cell.append(skeleton);
      row.append(cell);
    }
    elements.resultsBody.append(row);
  }
}

function renderRows(points) {
  elements.resultsBody.replaceChildren();
  elements.emptyState.hidden = points.length !== 0;

  points.forEach((point) => {
    const row = document.createElement("tr");

    const identityCell = document.createElement("td");
    const identity = document.createElement("div");
    identity.className = "point-name";
    const code = document.createElement("strong");
    code.textContent = point.ma_diem;
    const name = document.createElement("span");
    name.textContent = point.ten_diem || "Chưa có tên điểm";
    identity.append(code, name);
    identityCell.append(identity);

    const typeCell = document.createElement("td");
    const type = document.createElement("span");
    type.className = "tag";
    type.textContent = displayValue(point.loai_diem);
    typeCell.append(type);

    const locationCell = document.createElement("td");
    locationCell.textContent = displayValue(point.tinh);

    const routeCell = document.createElement("td");
    routeCell.textContent = displayValue(point.ma_tuyen);

    const deviceCell = document.createElement("td");
    deviceCell.textContent = displayValue(point.thiet_bi);

    const statusCell = document.createElement("td");
    const status = document.createElement("span");
    status.className = `status ${statusClass(point.trang_thai)}`;
    status.textContent = displayValue(point.trang_thai);
    statusCell.append(status);

    const actionCell = document.createElement("td");
    const action = document.createElement("button");
    action.type = "button";
    action.className = "row-action";
    action.textContent = "Chi tiết";
    action.addEventListener("click", () => openPointDialog(point));
    actionCell.append(action);

    row.append(
      identityCell,
      typeCell,
      locationCell,
      routeCell,
      deviceCell,
      statusCell,
      actionCell,
    );
    elements.resultsBody.append(row);
  });
}

function updateSummary() {
  elements.summaryNumber.textContent = numberFormatter.format(state.total);
  elements.summaryLabel.textContent = state.exactCode ? "điểm được tìm thấy" : "điểm phù hợp";
}

function updatePagination(visibleCount) {
  const currentPage = Math.floor(state.offset / state.limit) + 1;
  const totalPages = Math.max(1, Math.ceil(state.total / state.limit));
  const start = state.total === 0 ? 0 : state.offset + 1;
  const end = state.offset + visibleCount;

  elements.paginationInfo.textContent = state.total === 0
    ? "Không có dữ liệu"
    : `${numberFormatter.format(start)}–${numberFormatter.format(end)} trên ${numberFormatter.format(state.total)} điểm`;
  elements.pageNumber.textContent = `Trang ${currentPage}/${totalPages}`;
  elements.previousPage.disabled = state.exactCode !== "" || state.offset === 0;
  elements.nextPage.disabled = state.exactCode !== "" || state.offset + state.limit >= state.total;
}

function displayValue(value) {
  return value === null || value === undefined || value === "" ? "—" : String(value);
}

function statusClass(status) {
  const normalized = String(status || "").toLocaleLowerCase("vi");
  if (normalized.includes("hoạt động")) return "active";
  if (normalized.includes("bảo trì")) return "maintenance";
  if (normalized.includes("sự cố")) return "incident";
  return "";
}

function formatDate(value) {
  if (!value) return "—";
  const [year, month, day] = value.split("-").map(Number);
  if (!year || !month || !day) return value;
  return new Intl.DateTimeFormat("vi-VN").format(new Date(year, month - 1, day));
}

function openPointDialog(point) {
  const fields = [
    ["Tên điểm", point.ten_diem],
    ["Loại điểm", point.loai_diem],
    ["Tỉnh / thành phố", point.tinh],
    ["Địa chỉ", point.dia_chi],
    ["Mã tuyến", point.ma_tuyen],
    ["Thứ tự trên tuyến", point.thu_tu],
    ["Trạng thái", point.trang_thai],
    ["Thiết bị", point.thiet_bi],
    ["Loại cáp", point.loai_cap],
    ["Số sợi", point.so_soi],
    ["Ngày vận hành", formatDate(point.ngay_van_hanh)],
    ["Tọa độ", point.vi_do != null && point.kinh_do != null ? `${point.vi_do}, ${point.kinh_do}` : null],
  ];

  elements.dialogTitle.textContent = point.ma_diem;
  elements.dialogBody.replaceChildren();

  fields.forEach(([label, value]) => {
    const item = document.createElement("div");
    item.className = "detail-item";
    const itemLabel = document.createElement("span");
    itemLabel.textContent = label;
    const itemValue = document.createElement("strong");
    itemValue.textContent = displayValue(value);
    item.append(itemLabel, itemValue);
    elements.dialogBody.append(item);
  });

  const hasCoordinates = point.vi_do != null && point.kinh_do != null;
  elements.mapLink.hidden = !hasCoordinates;
  if (hasCoordinates) {
    elements.mapLink.href = `https://www.google.com/maps?q=${encodeURIComponent(`${point.vi_do},${point.kinh_do}`)}`;
  }

  elements.dialog.showModal();
}

function showNotice(message) {
  elements.notice.textContent = message;
  elements.notice.hidden = false;
}

function hideNotice() {
  elements.notice.hidden = true;
  elements.notice.textContent = "";
}

elements.filterForm.addEventListener("submit", (event) => {
  event.preventDefault();
  state.offset = 0;
  readFilters();
  loadPoints();
});

elements.resetButton.addEventListener("click", () => {
  elements.filterForm.reset();
  state.offset = 0;
  readFilters();
  loadPoints();
});

elements.pageSize.addEventListener("change", () => {
  state.limit = Number(elements.pageSize.value);
  state.offset = 0;
  loadPoints();
});

elements.previousPage.addEventListener("click", () => {
  state.offset = Math.max(0, state.offset - state.limit);
  loadPoints();
});

elements.nextPage.addEventListener("click", () => {
  if (state.offset + state.limit < state.total) {
    state.offset += state.limit;
    loadPoints();
  }
});

elements.dialogClose.addEventListener("click", () => elements.dialog.close());
elements.dialogDone.addEventListener("click", () => elements.dialog.close());
elements.dialog.addEventListener("click", (event) => {
  if (event.target === elements.dialog) elements.dialog.close();
});

elements.chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = elements.chatMessage.value.trim();
  if (!message) {
    elements.chatMessage.focus();
    return;
  }

  elements.chatSubmit.disabled = true;
  elements.chatSubmit.textContent = "Đang đối chiếu…";
  elements.chatAnswer.hidden = false;
  elements.chatAnswer.textContent = "Hệ thống đang truy vấn và đối chiếu dữ liệu, vui lòng chờ trong ít giây.";

  try {
    const payload = await apiRequest("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    const answer = payload.data.answer.replaceAll("**", "");
    const seconds = Math.max(0.1, payload.data.timing.total_ms / 1000).toFixed(1);
    elements.chatAnswer.textContent = `${answer}\n\nHoàn tất trong ${seconds} giây.`;
  } catch (error) {
    elements.chatAnswer.textContent = error.message;
  } finally {
    elements.chatSubmit.disabled = false;
    elements.chatSubmit.textContent = "Gửi câu hỏi";
  }
});

readFilters();
checkSystem();
loadPoints();
