let currentQuest = null;
let currentBrief = null;

const briefForm = document.getElementById("brief-form");
const statusEl = document.getElementById("status");
const questViewEl = document.getElementById("quest-view");
const jsonOutputEl = document.getElementById("json-output");
const regenControlsEl = document.getElementById("regenerate-controls");
const regenButtons = regenControlsEl.querySelectorAll("button[data-section]");
const regenStepButton = document.getElementById("regenerate-step-button");
const stepIndexInput = document.getElementById("step-index");

function setStatus(message, type = "") {
  statusEl.textContent = message;
  statusEl.className = "status";
  if (type) {
    statusEl.classList.add(type);
  }
}

function formToBrief() {
  const zone = document.getElementById("zone").value.trim();
  const faction = document.getElementById("faction").value.trim();
  const tone = document.getElementById("tone").value.trim();
  const player_level_min = parseInt(
    document.getElementById("level-min").value,
    10
  );
  const player_level_max = parseInt(
    document.getElementById("level-max").value,
    10
  );
  const narrative_style =
    document.getElementById("style").value.trim() || null;
  const number_of_steps =
    parseInt(document.getElementById("steps").value, 10) || 4;
  const target_playtime_minutesRaw =
    document.getElementById("playtime").value;
  const target_playtime_minutes = target_playtime_minutesRaw
    ? parseInt(target_playtime_minutesRaw, 10)
    : null;
  const forbiddenRaw =
    document.getElementById("forbidden").value.trim();
  const forbidden_elements =
    forbiddenRaw.length > 0
      ? forbiddenRaw
          .split(",")
          .map((s) => s.trim())
          .filter((s) => s.length > 0)
      : null;

  return {
    zone,
    faction,
    tone,
    player_level_min,
    player_level_max,
    narrative_style,
    number_of_steps,
    target_playtime_minutes,
    forbidden_elements,
  };
}

function renderQuest(quest) {
  if (!quest) {
    questViewEl.classList.add("empty");
    questViewEl.innerHTML =
      'No quest generated yet. Fill out the brief and click <strong>Generate Quest</strong>.';
    jsonOutputEl.textContent =
      "// Generated quest JSON will appear here";
    regenControlsEl.classList.add("hidden");
    return;
  }

  questViewEl.classList.remove("empty");
  let html = "";
  html += `<h3>${quest.title}</h3>`;
  html += `<p>${quest.summary}</p>`;
  html += `<div class="quest-meta">
    <span><strong>Zone:</strong> ${quest.zone}</span> |
    <span><strong>Faction:</strong> ${quest.faction}</span> |
    <span><strong>Tone:</strong> ${quest.tone}</span> |
    <span><strong>Levels:</strong> ${quest.player_level_min}-${quest.player_level_max}</span>
  </div>`;

  if (quest.steps && quest.steps.length > 0) {
    html += `<div class="quest-steps">`;
    quest.steps.forEach((step) => {
      html += `<div class="quest-step">
        <h4>Step ${step.step_number}: ${step.description}</h4>
        <p><strong>Objective:</strong> ${step.objective}</p>`;
      if (step.npc_dialogue && step.npc_dialogue.length > 0) {
        html += `<div class="quest-dialogue">`;
        step.npc_dialogue.forEach((line) => {
          html += `<p><span class="speaker">${line.speaker}:</span> ${line.text}</p>`;
        });
        html += `</div>`;
      }
      html += `</div>`;
    });
    html += `</div>`;
  }

  if (quest.rewards && quest.rewards.length > 0) {
    const rewardsStr = quest.rewards
      .map(
        (r) =>
          `${r.type.toUpperCase()}: ${r.description}${
            r.amount ? " (" + r.amount + ")" : ""
          }`
      )
      .join(" | ");
    html += `<p><strong>Rewards:</strong> ${rewardsStr}</p>`;
  }

  questViewEl.innerHTML = html;
  jsonOutputEl.textContent = JSON.stringify(quest, null, 2);
  regenControlsEl.classList.remove("hidden");
}

async function generateQuest(event) {
  event.preventDefault();
  const brief = formToBrief();
  currentBrief = brief;
  currentQuest = null;
  renderQuest(null);
  setStatus("Generating quest...", "loading");

  try {
    const resp = await fetch("/api/quests/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(brief),
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(
        err.detail || `Request failed with status ${resp.status}`
      );
    }

    const quest = await resp.json();
    currentQuest = quest;
    renderQuest(quest);
    setStatus("Quest generated successfully.", "success");
  } catch (err) {
    console.error(err);
    setStatus(`Error: ${err.message}`, "error");
  }
}

async function regenerate(section, stepIndex = null) {
  if (!currentQuest || !currentBrief) {
    setStatus("No quest to regenerate. Generate a quest first.", "error");
    return;
  }

  setStatus(`Regenerating ${section}...`, "loading");

  const payload = {
    brief: currentBrief,
    quest: currentQuest,
    section,
    step_index: stepIndex,
  };

  try {
    const resp = await fetch("/api/quests/regenerate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(
        err.detail || `Request failed with status ${resp.status}`
      );
    }

    const quest = await resp.json();
    currentQuest = quest;
    renderQuest(quest);
    setStatus(`Successfully regenerated ${section}.`, "success");
  } catch (err) {
    console.error(err);
    setStatus(`Error: ${err.message}`, "error");
  }
}

briefForm.addEventListener("submit", generateQuest);

regenButtons.forEach((btn) => {
  const section = btn.getAttribute("data-section");
  btn.addEventListener("click", () => regenerate(section));
});

regenStepButton.addEventListener("click", () => {
  const idxRaw = stepIndexInput.value;
  const idx = idxRaw ? parseInt(idxRaw, 10) : 0;
  regenerate("steps", idx);
});

renderQuest(null);
