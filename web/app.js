// Веб-клиент "Сделай себя лучше". Без сборки: index.html + styles.css + этот модуль.
// Экраны переключаются по хэшу: #/today, #/plan, #/workout, #/result/<id>, #/profile, #/onboarding.

const app = document.getElementById("app");
const topbar = document.getElementById("topbar");
const toastEl = document.getElementById("toast");

const DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];
const NEXT_DAY = {
  1: "в понедельник",
  2: "во вторник",
  3: "в среду",
  4: "в четверг",
  5: "в пятницу",
  6: "в субботу",
  7: "в воскресенье",
};
const FOCUS = {
  push: "Грудь, плечи, трицепс",
  pull: "Спина и бицепс",
  legs: "Ноги",
  upper: "Верх тела",
  lower: "Низ тела",
  full_body: "Всё тело",
};
const LEVELS = [
  ["beginner", "Начальный"],
  ["intermediate", "Средний"],
  ["hard", "Сложный"],
];
const GOALS = {
  up_weight: "Набрать массу",
  lose_weight: "Сбросить вес",
};

// ---------- Хранилище браузера ----------
// Ручки входа в API нет, поэтому id пользователя и идущая тренировка живут здесь.

const store = {
  get(key) {
    try {
      return JSON.parse(localStorage.getItem(key));
    } catch {
      return null;
    }
  },
  set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // без localStorage приложение работает до перезагрузки страницы
    }
  },
  remove(key) {
    try {
      localStorage.removeItem(key);
    } catch {
      // см. выше
    }
  },
};

let userId = store.get("userId");

function saveUser(id) {
  userId = id;
  store.set("userId", id);
}

function forgetUser() {
  userId = null;
  draft = emptyDraft();
  step = 1;
  ["userId", "activeWorkout", "planStale"].forEach((key) => store.remove(key));
}

// ---------- API ----------

class ApiError extends Error {
  constructor(status, detail) {
    super(detail);
    this.status = status;
    this.detail = detail;
    this.handled = false;
  }
}

async function api(method, path, body) {
  let response;
  try {
    response = await fetch(path, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(0, "network");
  }
  if (response.ok) {
    return response.status === 204 ? null : response.json();
  }
  const data = await response.json().catch(() => ({}));
  const error = new ApiError(response.status, data.detail);
  if (response.status === 404 && data.detail === "User not found") {
    // Пользователя удалили, а браузер ещё помнит его id: начинаем заново
    error.handled = true;
    forgetUser();
    toast("Аккаунт не найден, заполните анкету заново");
    location.hash = "#/onboarding";
  }
  throw error;
}

async function orNull(promise) {
  try {
    return await promise;
  } catch (error) {
    if (error.status === 404) return null;
    throw error;
  }
}

function errorText(error) {
  if (error.status === 0) return "Нет связи с сервером. Проверьте интернет и повторите.";
  if (error.status === 422) return "Сервер не принял данные. Проверьте поля и повторите.";
  return "Не удалось выполнить действие. Попробуйте ещё раз.";
}

// ---------- Общие части интерфейса ----------

function esc(value) {
  const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
  return String(value ?? "").replace(/[&<>"']/g, (char) => map[char]);
}

let toastTimer;
function toast(text) {
  toastEl.textContent = text;
  toastEl.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastEl.hidden = true;
  }, 4000);
}

function loading(title) {
  app.innerHTML = `
    <section class="card narrow">
      <h1 class="subtitle">${esc(title)}</h1>
      <div class="skeleton"></div>
      <div class="skeleton"></div>
      <div class="skeleton"></div>
    </section>`;
}

function showFailure(error) {
  if (error.handled) return;
  const offline = error.status === 0;
  app.innerHTML = `
    <section class="card narrow">
      <h1 class="title">${offline ? "Нет связи с сервером" : "Что-то пошло не так"}</h1>
      <p class="muted">${offline ? "Проверьте интернет и попробуйте ещё раз." : "Попробуйте ещё раз чуть позже."}</p>
      <button class="btn" id="retry">Повторить</button>
    </section>`;
  document.getElementById("retry").addEventListener("click", route);
}

function showNoPlan() {
  app.innerHTML = `
    <section class="card narrow">
      <h1 class="title">Плана пока нет</h1>
      <p class="muted">Выберите уровень и дни, и мы соберём план.</p>
      <a class="btn btn--primary" href="#/onboarding">Заполнить анкету</a>
    </section>`;
}

async function withBusy(button, label, action) {
  const original = button.textContent;
  button.disabled = true;
  button.textContent = label;
  try {
    return await action();
  } finally {
    button.disabled = false;
    button.textContent = original;
  }
}

function exerciseAmount(exercise) {
  return exercise.minutes ? `${exercise.minutes} мин` : `${exercise.sets} × ${exercise.reps}`;
}

function formatNumber(value) {
  return value === undefined || value === null || value === "" ? "" : String(Number(value));
}

function todayNumber() {
  return new Date().getDay() || 7; // в JS воскресенье это 0, в API это 7
}

// ---------- Поля форм ----------

function field(name, label, value, hint = "", inputmode = "decimal") {
  return `
    <label class="field" data-field="${name}">${esc(label)}
      <input name="${name}" value="${esc(value)}" inputmode="${inputmode}" autocomplete="off">
      ${hint ? `<span class="field__hint">${esc(hint)}</span>` : ""}
      <span class="field__error" data-error="${name}" hidden></span>
    </label>`;
}

function choices(name, label, options, selected, className = "cols-2") {
  const buttons = options
    .map(([value, text, small]) => {
      const pressed = String(selected) === String(value);
      return `<button type="button" class="choice" data-value="${value}" aria-pressed="${pressed}">${esc(text)}${small ? `<small>${esc(small)}</small>` : ""}</button>`;
    })
    .join("");
  return `
    <div>
      <div class="${className}" role="group" aria-label="${esc(label)}" data-choice="${name}">${buttons}</div>
      <span class="field__error" data-error="${name}" hidden></span>
    </div>`;
}

function dayChoices(selected = []) {
  const buttons = DAYS.map((day, index) => {
    const value = index + 1;
    return `<button type="button" class="choice" data-value="${value}" aria-pressed="${selected.includes(value)}">${day}</button>`;
  }).join("");
  return `
    <div>
      <div class="days" role="group" aria-label="Дни тренировок" data-days>${buttons}</div>
      <span class="field__error" data-error="days" hidden></span>
    </div>`;
}

function paramsFields(values) {
  return `
    ${choices("gender", "Пол", [["male", "Мужской"], ["female", "Женский"]], values.gender)}
    <div class="cols-3">
      ${field("age", "Возраст", formatNumber(values.age), "", "numeric")}
      ${field("weight", "Вес, кг", formatNumber(values.weight))}
      ${field("height", "Рост, см", formatNumber(values.height), "", "numeric")}
    </div>`;
}

function goalFields(values, withReps = false) {
  const options = [
    ["up_weight", GOALS.up_weight, withReps ? "8 повторений в подходе" : ""],
    ["lose_weight", GOALS.lose_weight, withReps ? "15 повторений в подходе" : ""],
  ];
  return `
    ${choices("goal_type", "Цель", options, values.goal_type)}
    ${field("target_weight", "Желаемый вес, кг", formatNumber(values.target_weight), "Не больше 120 кг")}`;
}

function settingsFields(values) {
  return `
    ${choices("level", "Уровень", LEVELS, values.level, "cols-3")}
    ${dayChoices(values.days)}`;
}

// Клик по вариантам: один выбор в группе, в днях можно выбрать несколько
app.addEventListener("click", (event) => {
  const button = event.target.closest(".choice");
  if (!button) return;
  const group = button.parentElement;
  if (group.hasAttribute("data-days")) {
    button.setAttribute("aria-pressed", String(button.getAttribute("aria-pressed") !== "true"));
    return;
  }
  group.querySelectorAll(".choice").forEach((item) => {
    item.setAttribute("aria-pressed", String(item === button));
  });
});

function readChoice(root, name) {
  return root.querySelector(`[data-choice="${name}"] [aria-pressed="true"]`)?.dataset.value ?? null;
}

function readDays(root) {
  return [...root.querySelectorAll('[data-days] [aria-pressed="true"]')].map((item) =>
    Number(item.dataset.value),
  );
}

function readInput(root, name) {
  return root.querySelector(`[name="${name}"]`).value.trim();
}

// Границы совпадают со схемами Pydantic в src/*/schemas.py
function parseDecimal(text, max) {
  const normalized = text.replace(",", ".");
  if (!/^\d{1,3}(\.\d{1,2})?$/.test(normalized)) return null;
  const number = Number(normalized);
  return number > 0 && number <= max ? normalized : null;
}

function parseIntInRange(text, min, max) {
  if (!/^\d{1,3}$/.test(text)) return null;
  const number = Number(text);
  return number >= min && number <= max ? number : null;
}

function readParams(root) {
  const values = {
    gender: readChoice(root, "gender"),
    age: parseIntInRange(readInput(root, "age"), 1, 99),
    weight: parseDecimal(readInput(root, "weight"), 150),
    height: parseIntInRange(readInput(root, "height"), 101, 220),
  };
  const errors = {};
  if (!values.gender) errors.gender = "Выберите пол";
  if (values.age === null) errors.age = "От 1 до 99";
  if (values.weight === null) errors.weight = "До 150 кг";
  if (values.height === null) errors.height = "От 101 до 220";
  return { values, errors };
}

function readGoal(root) {
  const values = {
    goal_type: readChoice(root, "goal_type"),
    target_weight: parseDecimal(readInput(root, "target_weight"), 120),
  };
  const errors = {};
  if (!values.goal_type) errors.goal_type = "Выберите цель";
  if (values.target_weight === null) errors.target_weight = "Укажите вес: больше 0 и не больше 120 кг";
  return { values, errors };
}

function readSettings(root) {
  const values = { level: readChoice(root, "level"), days: readDays(root) };
  const errors = {};
  if (!values.level) errors.level = "Выберите уровень";
  if (!values.days.length) errors.days = "Выберите хотя бы один день";
  return { values, errors };
}

// Показывает ошибки полей. Возвращает true, если ошибок нет.
function showErrors(root, errors) {
  root.querySelectorAll("[data-error]").forEach((element) => {
    const message = errors[element.dataset.error];
    element.textContent = message ?? "";
    element.hidden = !message;
    element.closest(".field")?.classList.toggle("field--invalid", Boolean(message));
  });
  return Object.keys(errors).length === 0;
}

// ---------- Анкета ----------

function emptyDraft() {
  return { username: "", gender: null, age: "", weight: "", height: "", goal_type: null, target_weight: "", level: null, days: [] };
}

let draft = emptyDraft();
let step = 1;

function pageOnboarding() {
  if (userId && step === 1) step = 2; // аккаунт уже создан, имя повторно не спрашиваем
  const first = userId ? 2 : 1;
  const number = userId ? step - 1 : step;
  const total = userId ? 3 : 4;
  const screens = {
    1: {
      title: "Сделай себя лучше",
      body: `
        <p class="muted">План тренировок под вашу цель и удобные дни. Анкета займёт пару минут.</p>
        ${field("username", "Как вас зовут?", draft.username, "До 18 символов", "text")}`,
    },
    2: {
      title: "О вас",
      body: `
        ${paramsFields(draft)}
        <div class="hint">Вес нужен, чтобы считать калории за тренировку.</div>`,
    },
    3: { title: "Ваша цель", body: goalFields(draft, true) },
    4: {
      title: "Уровень и дни",
      body: `
        ${settingsFields(draft)}
        <div class="hint">Новичку хватит 2–3 дней в неделю, между тренировками лучше оставлять день отдыха.</div>`,
    },
  };
  const screen = screens[step];
  app.innerHTML = `
    <form class="card narrow" id="onboarding" novalidate>
      <div class="eyebrow">Шаг ${number} из ${total}</div>
      <h1 class="title">${screen.title}</h1>
      ${screen.body}
      <p class="error" id="form-error" hidden></p>
      <div class="${step > first ? "actions" : ""} push-down">
        ${step > first ? '<button type="button" class="btn" id="back">Назад</button>' : ""}
        <button class="btn btn--primary" id="next">${step === 4 ? "Собрать план" : "Дальше"}</button>
      </div>
    </form>`;

  const form = document.getElementById("onboarding");

  function collect() {
    if (step === 1) {
      const username = readInput(form, "username");
      draft.username = username;
      return !username || username.length > 18 ? { username: "Имя от 1 до 18 символов" } : {};
    }
    const raw = step === 2 ? readParams(form) : step === 3 ? readGoal(form) : readSettings(form);
    Object.assign(draft, raw.values);
    return raw.errors;
  }

  document.getElementById("back")?.addEventListener("click", () => {
    collect();
    step -= 1;
    pageOnboarding();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!showErrors(form, collect())) return;
    if (step < 4) {
      step += 1;
      pageOnboarding();
      return;
    }
    const errorEl = document.getElementById("form-error");
    errorEl.hidden = true;
    try {
      await withBusy(document.getElementById("next"), "Собираем план…", submitOnboarding);
      draft = emptyDraft();
      step = 1;
      location.hash = "#/today";
    } catch (error) {
      if (error.handled) {
        pageOnboarding();
        return;
      }
      errorEl.textContent = errorText(error);
      errorEl.hidden = false;
    }
  });
}

async function submitOnboarding() {
  // id сохраняем сразу: при повторе после сбоя второй аккаунт не появится
  if (!userId) {
    const user = await api("POST", "/users/", { username: draft.username });
    saveUser(user.id);
  }
  const { gender, age, weight, height, goal_type, target_weight, level, days } = draft;
  await api("POST", "/users/parameters/", { user_id: userId, gender, age, weight, height });
  await api("POST", "/users/goals/", { user_id: userId, goal_type, target_weight });
  await api("POST", "/users/training-settings/", { user_id: userId, level, days });
  await api("POST", `/users/training-plan/${userId}/regenerate`);
  store.remove("planStale");
}

// ---------- Сегодня ----------

async function pageToday(alive) {
  loading("Загружаем план…");
  let plan, goal, params;
  try {
    [plan, goal, params] = await Promise.all([
      api("GET", `/users/training-plan/${userId}`),
      orNull(api("GET", `/users/goals/${userId}`)),
      orNull(api("GET", `/users/parameters/${userId}`)),
    ]);
  } catch (error) {
    if (!alive()) return;
    if (error.status === 404 && !error.handled) showNoPlan();
    else showFailure(error);
    return;
  }
  if (!alive()) return;

  const today = todayNumber();
  const trainingDays = plan.days.map((item) => item.day);
  const week = DAYS.map((name, index) => {
    const day = index + 1;
    const className = day === today ? "week--today" : trainingDays.includes(day) ? "week--on" : "";
    return `<div class="${className}">${name}</div>`;
  }).join("");

  const goalCard = goal
    ? `<section class="card">
        <h2 class="subtitle">Цель</h2>
        <div class="big">${formatNumber(goal.target_weight)} кг</div>
        <div class="muted">${GOALS[goal.goal_type] ?? ""}${params ? `, сейчас ${formatNumber(params.weight)} кг` : ""}</div>
      </section>`
    : "";

  const planned = plan.days.find((item) => item.day === today);
  app.innerHTML = `
    <div class="layout">
      <section class="card layout__main" id="today-card">${planned ? todayWorkout(planned) : restDay(plan, today)}</section>
      <aside class="layout__side">
        <section class="card">
          <h2 class="subtitle">Неделя</h2>
          <div class="week">${week}</div>
        </section>
        ${goalCard}
        <div class="hint">Калории посчитаем сами, когда вы завершите тренировку.</div>
      </aside>
    </div>`;

  document.getElementById("start")?.addEventListener("click", (event) => startWorkout(event.currentTarget, planned));
}

function todayWorkout(day) {
  const rows = day.exercises
    .map((exercise) => `<li><span>${esc(exercise.name)}</span><strong class="nowrap">${exerciseAmount(exercise)}</strong></li>`)
    .join("");
  const action = store.get("activeWorkout")
    ? '<a class="btn btn--primary btn--large" href="#/workout">Вернуться к тренировке</a>'
    : '<button class="btn btn--primary btn--large" id="start">Начать тренировку</button>';
  return `
    <div>
      <div class="eyebrow">${esc(day.day_name)}</div>
      <h1 class="title">${esc(FOCUS[day.focus] ?? day.focus)}</h1>
    </div>
    <ol class="rows">${rows}</ol>
    <p class="error" id="start-error" hidden></p>
    ${action}`;
}

function restDay(plan, today) {
  const next = plan.days.find((item) => item.day > today) ?? plan.days[0];
  const about = next
    ? `<p class="muted">Следующая тренировка ${NEXT_DAY[next.day]}: ${esc((FOCUS[next.focus] ?? next.focus).toLowerCase())}.</p>`
    : "";
  return `
    <h1 class="title">Сегодня отдых</h1>
    ${about}
    <a class="btn push-down" href="#/plan">Посмотреть план</a>`;
}

async function startWorkout(button, day) {
  const errorEl = document.getElementById("start-error");
  errorEl.hidden = true;
  try {
    const workout = await withBusy(button, "Начинаем…", () =>
      api("POST", "/workouts/start-train", { user_id: userId }),
    );
    store.set("activeWorkout", { id: workout.id, startedAt: workout.started_at, day, checked: [] });
    location.hash = "#/workout";
  } catch (error) {
    if (error.handled) return;
    if (error.status === 409) {
      showWorkoutAlreadyRunning();
      return;
    }
    errorEl.textContent = errorText(error);
    errorEl.hidden = false;
  }
}

function showWorkoutAlreadyRunning() {
  app.innerHTML = `
    <section class="card narrow">
      <h1 class="title">Тренировка уже идёт</h1>
      <p class="muted">Вы начали её раньше. Завершите её, чтобы начать новую.</p>
      <p class="error" id="finish-error" hidden></p>
      <button class="btn btn--primary" id="finish">Завершить тренировку</button>
    </section>`;
  document.getElementById("finish").addEventListener("click", (event) => finishWorkout(event.currentTarget));
}

// ---------- Тренировка ----------

let timer;

function pageWorkout() {
  const active = store.get("activeWorkout");
  if (!active) {
    location.hash = "#/today";
    return;
  }
  const checks = active.day.exercises
    .map((exercise, index) => `
      <label class="check">
        <input type="checkbox" data-index="${index}" ${active.checked.includes(index) ? "checked" : ""}>
        <span>${esc(exercise.name)}</span>
        <strong class="nowrap">${exerciseAmount(exercise)}</strong>
      </label>`)
    .join("");
  app.innerHTML = `
    <section class="card narrow">
      <div class="center">
        <div class="eyebrow">Идёт тренировка</div>
        <div class="huge" id="timer" role="timer">00:00:00</div>
      </div>
      <div class="checks">${checks}</div>
      <p class="error" id="finish-error" hidden></p>
      <button class="btn btn--primary btn--large" id="finish">Завершить тренировку</button>
      <p class="muted center">Страницу можно закрыть: время идёт на сервере</p>
    </section>`;

  const timerEl = document.getElementById("timer");
  const started = new Date(active.startedAt).getTime();
  const tick = () => {
    const total = Math.max(0, Math.floor((Date.now() - started) / 1000));
    const parts = [total / 3600, (total % 3600) / 60, total % 60].map((part) =>
      String(Math.floor(part)).padStart(2, "0"),
    );
    timerEl.textContent = parts.join(":");
  };
  tick();
  timer = setInterval(tick, 1000);

  app.querySelector(".checks").addEventListener("change", () => {
    active.checked = [...app.querySelectorAll(".check input:checked")].map((input) => Number(input.dataset.index));
    store.set("activeWorkout", active);
  });
  document.getElementById("finish").addEventListener("click", (event) => finishWorkout(event.currentTarget));
}

async function finishWorkout(button) {
  const errorEl = document.getElementById("finish-error");
  errorEl.hidden = true;
  try {
    const workout = await withBusy(button, "Считаем калории…", () =>
      api("POST", "/workouts/end-train", { user_id: userId }),
    );
    store.remove("activeWorkout");
    location.hash = `#/result/${workout.id}`;
  } catch (error) {
    if (error.handled) return;
    if (error.status === 404) {
      store.remove("activeWorkout");
      toast("Активной тренировки нет");
      location.hash = "#/today";
      route();
      return;
    }
    errorEl.textContent =
      error.status === 400 ? "Укажите вес в профиле, чтобы посчитать калории." : errorText(error);
    errorEl.hidden = false;
  }
}

async function pageResult(alive, workoutId) {
  loading("Считаем калории…");
  let result;
  try {
    result = await api("GET", `/workouts/${workoutId}/calories`);
  } catch (error) {
    if (alive()) showFailure(error);
    return;
  }
  if (!alive()) return;
  app.innerHTML = `
    <section class="card narrow">
      <h1 class="title">Готово!</h1>
      <div>
        <div class="huge">${Math.round(Number(result.calories))}</div>
        <div class="muted">ккал сожжено</div>
      </div>
      <dl class="stats">
        <dt>Длительность</dt><dd>${Math.round(result.duration_minutes)} мин</dd>
        <dt>Вес</dt><dd>${formatNumber(result.weight)} кг</dd>
        <dt>Интенсивность, MET</dt><dd>${formatNumber(result.met)}</dd>
      </dl>
      <div class="hint">Считаем так: MET × вес × часы. Это оценка, а не точное измерение.</div>
      <a class="btn" href="#/today">На главную</a>
    </section>`;
}

// ---------- План ----------

async function pagePlan(alive) {
  loading("Загружаем план…");
  let plan;
  try {
    plan = await api("GET", `/users/training-plan/${userId}`);
  } catch (error) {
    if (!alive()) return;
    if (error.status === 404 && !error.handled) showNoPlan();
    else showFailure(error);
    return;
  }
  if (alive()) renderPlan(plan);
}

function renderPlan(plan) {
  const today = todayNumber();
  const level = LEVELS.find(([value]) => value === plan.level)?.[1] ?? plan.level;
  const goal = GOALS[plan.goal_type];
  const summary = [`Уровень: ${level.toLowerCase()}`, goal && `цель: ${goal.toLowerCase()}`, `дней в неделю: ${plan.days.length}`]
    .filter(Boolean)
    .join(", ");
  const cards = plan.days
    .map((day) => {
      const isToday = day.day === today;
      const rows = day.exercises
        .map((exercise) => `<li><span>${esc(exercise.name)}</span><strong class="nowrap">${exerciseAmount(exercise)}</strong></li>`)
        .join("");
      return `
        <section class="card${isToday ? " card--now" : ""}">
          <div class="eyebrow${isToday ? " eyebrow--now" : ""}">${esc(day.day_name)}${isToday ? " · сегодня" : ""}</div>
          <h2 class="subtitle">${esc(FOCUS[day.focus] ?? day.focus)}</h2>
          <ul class="plan-list">${rows}</ul>
        </section>`;
    })
    .join("");
  const stale = store.get("planStale");
  app.innerHTML = `
    <div class="stack">
      <div class="head">
        <div>
          <h1 class="title">План на неделю</h1>
          <p class="muted">${esc(summary)}</p>
        </div>
        <button class="btn${stale ? " btn--primary" : ""}" id="regenerate">Пересобрать план</button>
      </div>
      <div class="grid">${cards}</div>
      <div class="hint">${stale ? "<strong>План устарел.</strong> Вы поменяли цель, уровень или дни: нажмите «Пересобрать план»." : "Сменили уровень, дни или цель? Нажмите «Пересобрать план»: сам он не обновится."}</div>
    </div>`;

  document.getElementById("regenerate").addEventListener("click", async (event) => {
    try {
      const fresh = await withBusy(event.currentTarget, "Пересобираем…", () =>
        api("POST", `/users/training-plan/${userId}/regenerate`),
      );
      store.remove("planStale");
      renderPlan(fresh);
      toast("План пересобран");
    } catch (error) {
      if (!error.handled) toast(errorText(error));
    }
  });
}

// ---------- Профиль ----------

async function pageProfile(alive) {
  loading("Загружаем профиль…");
  let params, goal, settings;
  try {
    [params, goal, settings] = await Promise.all([
      orNull(api("GET", `/users/parameters/${userId}`)),
      orNull(api("GET", `/users/goals/${userId}`)),
      orNull(api("GET", `/users/training-settings/${userId}`)),
    ]);
  } catch (error) {
    if (alive()) showFailure(error);
    return;
  }
  if (!alive()) return;

  app.innerHTML = `
    <div class="grid grid--wide">
      <form class="card" id="form-params" novalidate>
        <h2 class="subtitle">Параметры</h2>
        ${paramsFields(params ?? {})}
        <button class="btn push-down">Сохранить</button>
      </form>
      <form class="card" id="form-goal" novalidate>
        <h2 class="subtitle">Цель</h2>
        ${goalFields(goal ?? {})}
        <button class="btn push-down">Сохранить</button>
      </form>
      <form class="card" id="form-settings" novalidate>
        <h2 class="subtitle">Уровень и дни</h2>
        ${settingsFields(settings ?? { days: [] })}
        <button class="btn push-down">Сохранить</button>
      </form>
      <section class="card" id="account">
        <h2 class="subtitle">Аккаунт</h2>
        <p class="muted">Удаление нельзя отменить: пропадут параметры, цель, план и тренировки.</p>
        <button class="btn btn--danger push-down" id="delete">Удалить аккаунт</button>
      </section>
    </div>`;

  bindSave("form-params", readParams, "/users/parameters/", false);
  bindSave("form-goal", readGoal, "/users/goals/", true);
  bindSave("form-settings", readSettings, "/users/training-settings/", true);
  document.getElementById("delete").addEventListener("click", confirmDelete);
}

function bindSave(formId, read, path, affectsPlan) {
  const form = document.getElementById(formId);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const { values, errors } = read(form);
    if (!showErrors(form, errors)) return;
    try {
      await withBusy(form.querySelector("button:not(.choice)"), "Сохраняем…", () =>
        api("POST", path, { user_id: userId, ...values }),
      );
      if (affectsPlan) store.set("planStale", true);
      toast(affectsPlan ? "Сохранено. Пересоберите план во вкладке «План»" : "Сохранено");
    } catch (error) {
      if (!error.handled) toast(errorText(error));
    }
  });
}

function confirmDelete() {
  const account = document.getElementById("account");
  account.classList.add("card--danger");
  account.innerHTML = `
    <h2 class="subtitle">Удалить аккаунт?</h2>
    <p>Параметры, цель, план и тренировки пропадут. Это нельзя отменить.</p>
    <p class="error" id="delete-error" hidden></p>
    <div class="cols-2 push-down">
      <button class="btn" id="delete-cancel">Отмена</button>
      <button class="btn btn--danger-solid" id="delete-confirm">Удалить</button>
    </div>`;
  document.getElementById("delete-cancel").addEventListener("click", route);
  document.getElementById("delete-confirm").addEventListener("click", async (event) => {
    try {
      await withBusy(event.currentTarget, "Удаляем…", () => api("DELETE", `/users/${userId}`));
      forgetUser();
      toast("Аккаунт удалён");
      location.hash = "#/onboarding";
    } catch (error) {
      if (error.handled) return;
      const errorEl = document.getElementById("delete-error");
      errorEl.textContent = errorText(error);
      errorEl.hidden = false;
    }
  });
}

// ---------- Переключение экранов ----------

let routeToken = 0;

function route() {
  clearInterval(timer);
  const token = ++routeToken;
  const alive = () => token === routeToken;
  const [name, param] = location.hash.replace(/^#\//, "").split("/");

  if (!userId && name !== "onboarding") {
    location.hash = "#/onboarding";
    return;
  }
  const target = name || "today";
  const withTabs = ["today", "plan", "profile"].includes(target);
  topbar.hidden = !withTabs;
  topbar.querySelectorAll("[data-tab]").forEach((link) => {
    if (link.dataset.tab === target) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  window.scrollTo(0, 0);

  if (target === "onboarding") pageOnboarding();
  else if (target === "today") pageToday(alive);
  else if (target === "plan") pagePlan(alive);
  else if (target === "workout") pageWorkout();
  else if (target === "result") pageResult(alive, Number(param));
  else if (target === "profile") pageProfile(alive);
  else location.hash = "#/today";
}

window.addEventListener("hashchange", route);
route();
