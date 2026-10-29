"use strict";

const STORAGE_KEY = "todoItems";

const form = document.querySelector("#todo-form");
const input = document.querySelector("#todo-input");
const inputError = document.querySelector("#input-error");
const todoList = document.querySelector("#todo-list");
const emptyState = document.querySelector("#empty-state");
const filterButtons = [...document.querySelectorAll(".filter-button")];
const clearCompletedButton = document.querySelector("#clear-completed");
const todayLabel = document.querySelector("#today-label");

let todos = loadTodos();
let currentFilter = "all";

function loadTodos() {
  try {
    const storedTodos = localStorage.getItem(STORAGE_KEY);
    if (!storedTodos) return [];

    const parsedTodos = JSON.parse(storedTodos);
    if (!Array.isArray(parsedTodos)) return [];

    return parsedTodos.filter((todo) =>
      todo &&
      (typeof todo.id === "string" || typeof todo.id === "number") &&
      typeof todo.text === "string" &&
      typeof todo.completed === "boolean"
    );
  } catch (error) {
    console.warn("저장된 할 일을 불러오지 못했습니다:", error);
    return [];
  }
}

function saveTodos() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
  } catch (error) {
    console.warn("할 일을 저장하지 못했습니다:", error);
  }
}

function createId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function getFilteredTodos() {
  if (currentFilter === "active") return todos.filter((todo) => !todo.completed);
  if (currentFilter === "completed") return todos.filter((todo) => todo.completed);
  return todos;
}

function escapeText(text) {
  const element = document.createElement("span");
  element.textContent = text;
  return element.innerHTML;
}

function render() {
  const filteredTodos = getFilteredTodos();
  todoList.replaceChildren();

  filteredTodos.forEach((todo) => {
    const item = document.createElement("li");
    item.className = `todo-item${todo.completed ? " completed" : ""}`;
    item.dataset.id = String(todo.id);

    const checkbox = document.createElement("input");
    checkbox.className = "todo-checkbox";
    checkbox.type = "checkbox";
    checkbox.checked = todo.completed;
    checkbox.setAttribute("aria-label", `${todo.text} 완료 상태`);

    const text = document.createElement("span");
    text.className = "todo-text";
    text.innerHTML = escapeText(todo.text);

    const deleteButton = document.createElement("button");
    deleteButton.className = "delete-button";
    deleteButton.type = "button";
    deleteButton.textContent = "×";
    deleteButton.setAttribute("aria-label", `${todo.text} 삭제`);

    item.append(checkbox, text, deleteButton);
    todoList.append(item);
  });

  emptyState.classList.toggle("hidden", filteredTodos.length > 0);
  const emptyMessage = emptyState.querySelector("p");
  emptyMessage.textContent = filteredTodos.length === 0 && todos.length > 0
    ? "표시할 할 일이 없습니다."
    : "등록된 할 일이 없습니다.";

  updateCounts();
}

function updateCounts() {
  const completedCount = todos.filter((todo) => todo.completed).length;
  const activeCount = todos.length - completedCount;
  document.querySelector("#count-all").textContent = todos.length;
  document.querySelector("#count-active").textContent = activeCount;
  document.querySelector("#count-completed").textContent = completedCount;
  document.querySelector("#progress-percent").textContent = todos.length === 0
    ? "0%"
    : `${Math.round((completedCount / todos.length) * 100)}%`;
  clearCompletedButton.disabled = completedCount === 0;
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();

  if (!text) {
    inputError.textContent = "할 일을 입력하세요.";
    input.focus();
    return;
  }

  todos.unshift({
    id: createId(),
    text,
    completed: false,
    createdAt: new Date().toISOString(),
  });

  saveTodos();
  input.value = "";
  inputError.textContent = "";
  currentFilter = "all";
  updateFilterButtons();
  render();
  input.focus();
});

input.addEventListener("input", () => {
  inputError.textContent = "";
});

todoList.addEventListener("change", (event) => {
  if (!event.target.matches(".todo-checkbox")) return;
  const item = event.target.closest(".todo-item");
  const todo = todos.find((entry) => String(entry.id) === item.dataset.id);
  if (!todo) return;

  todo.completed = event.target.checked;
  saveTodos();
  render();
});

todoList.addEventListener("click", (event) => {
  const deleteButton = event.target.closest(".delete-button");
  if (!deleteButton) return;
  const item = deleteButton.closest(".todo-item");
  todos = todos.filter((todo) => String(todo.id) !== item.dataset.id);
  saveTodos();
  render();
});

function updateFilterButtons() {
  filterButtons.forEach((button) => {
    const selected = button.dataset.filter === currentFilter;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
}

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    currentFilter = button.dataset.filter;
    updateFilterButtons();
    render();
  });
});

clearCompletedButton.addEventListener("click", () => {
  todos = todos.filter((todo) => !todo.completed);
  saveTodos();
  render();
});

const dateFormatter = new Intl.DateTimeFormat("ko-KR", {
  year: "numeric",
  month: "long",
  day: "numeric",
  weekday: "long",
});
todayLabel.textContent = dateFormatter.format(new Date());

render();
