/**
 * DNA Clinical Diagnostic Workspace - Multi-Investigation Controller
 */

let modulesData = [];
let activeModule = null;
let currentPrediction = null;
let pinnedPrediction = null;
let revisionCounter = 0;

const el = id => document.getElementById(id);

function textNode(tag, text, className) {
  const node = document.createElement(tag);
  node.textContent = text;
  if (className) node.className = className;
  return node;
}

// 1. Initialize application
async function initApp() {
  try {
    const response = await fetch('/api/modules');
    if (!response.ok) throw new Error('Failed to load clinical diagnostic modules.');
    const data = await response.json();
    modulesData = data.modules || [];

    if (!modulesData.length) {
      el('error').textContent = 'No diagnostic modules available.';
      el('error').hidden = false;
      return;
    }

    renderInvestigationCards();
    renderSidebarTestList();

    // Default to the first module (HCV) or user preference
    switchModule(modulesData[0].id);
  } catch (err) {
    el('error').textContent = 'Initialization error: ' + err.message;
    el('error').hidden = false;
  }
}

// 2. Render Investigation Selector Cards
function renderInvestigationCards() {
  const container = el('test-cards-container');
  container.replaceChildren();

  modulesData.forEach(mod => {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'test-card';
    card.id = `card-${mod.id}`;
    card.setAttribute('role', 'tab');
    card.setAttribute('aria-selected', 'false');

    const top = document.createElement('div');
    top.className = 'test-card-top';

    const icon = textNode('span', mod.icon, 'test-card-icon');
    const badge = textNode('span', mod.organ, 'test-card-organ');
    top.append(icon, badge);

    const title = textNode('h3', mod.test_name, 'test-card-title');
    const tagline = textNode('p', mod.tagline, 'test-card-tagline');

    const meta = document.createElement('div');
    meta.className = 'test-card-meta';
    const params = textNode('span', `${mod.fields.length} Parameters`, 'test-card-count');
    const acc = textNode(
      'span',
      `Accuracy: ${(mod.metrics.accuracy * 100).toFixed(1)}%`,
      'test-card-acc'
    );
    meta.append(params, acc);

    card.append(top, title, tagline, meta);

    card.onclick = () => switchModule(mod.id);
    container.append(card);
  });
}

// 3. Render Sidebar Test Quick Switchers
function renderSidebarTestList() {
  const container = el('sidebar-test-list');
  container.replaceChildren();

  modulesData.forEach(mod => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'sidebar-test-btn';
    btn.id = `side-btn-${mod.id}`;

    const icon = textNode('span', mod.icon, 'sidebar-test-icon');
    const name = textNode('span', mod.short_name, 'sidebar-test-name');
    btn.append(icon, name);

    btn.onclick = () => switchModule(mod.id);
    container.append(btn);
  });
}

// 4. Switch Active Diagnostic Investigation
function switchModule(modId) {
  const mod = modulesData.find(m => m.id === modId);
  if (!mod) return;

  activeModule = mod;
  revisionCounter++;
  currentPrediction = null;
  pinnedPrediction = null;

  // Update UI Card States
  modulesData.forEach(m => {
    const card = el(`card-${m.id}`);
    if (card) {
      card.classList.toggle('active', m.id === modId);
      card.setAttribute('aria-selected', m.id === modId ? 'true' : 'false');
    }
    const sideBtn = el(`side-btn-${m.id}`);
    if (sideBtn) {
      sideBtn.classList.toggle('active', m.id === modId);
    }
  });

  // Update Topbar and Headers
  el('topbar-investigation-name').textContent = mod.test_name;
  el('sidebar-card-title').textContent = mod.test_name;
  el('sidebar-card-desc').textContent = mod.clinical_focus;
  el('sidebar-card-badge').textContent = mod.organ.toUpperCase();
  el('form-panel-title').textContent = `${mod.short_name} Panel`;
  el('feature-count-badge').textContent = `${mod.fields.length} Parameters`;
  el('test-clinical-hint').textContent = `${mod.clinical_focus} Maximum allowed missing parameters for this panel: ${mod.max_missing}.`;
  el('empty-icon').textContent = mod.icon;

  // Clear Results
  el('result').hidden = true;
  el('empty-result').hidden = false;
  el('explanation').hidden = true;
  el('explanation-empty').hidden = false;
  el('error').hidden = true;
  el('result-status').textContent = 'Awaiting test inputs';
  showComparison();

  // Populate Examples Dropdown
  const exampleSelect = el('example');
  exampleSelect.replaceChildren();
  if (mod.examples && mod.examples.length) {
    mod.examples.forEach((sample, idx) => {
      const opt = document.createElement('option');
      opt.value = idx;
      opt.textContent = `${sample.case_label || `Sample #${sample.sample_id}`} (Held-out)`;
      exampleSelect.append(opt);
    });
  } else {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = 'No preset cases available';
    exampleSelect.append(opt);
  }

  // Render Form Fields
  renderFormFields(mod);

  // Update Evaluation Section
  updateEvaluationSection(mod);

  // Update Footers
  el('footer-source-link').href = mod.source;
  el('footer-sample-csv').href = `/artifacts/${mod.id}/example_inputs.csv`;
}

// 5. Render Form Fields Grouped by Category
function renderFormFields(mod) {
  const container = el('form-fields-container');
  container.replaceChildren();

  // Group fields by category
  const categories = {};
  mod.fields.forEach(f => {
    const cat = f.category || 'Clinical Observations';
    if (!categories[cat]) categories[cat] = [];
    categories[cat].push(f);
  });

  // Render each category group
  Object.entries(categories).forEach(([categoryName, fields]) => {
    const section = document.createElement('div');
    section.className = 'form-section';

    const header = document.createElement('div');
    header.className = 'section-label lab-heading';
    header.textContent = categoryName.toUpperCase();
    section.append(header);

    const grid = document.createElement('div');
    grid.className = 'lab-grid';

    fields.forEach(field => {
      const label = document.createElement('label');
      label.className = 'field-wrapper';

      const head = document.createElement('div');
      head.className = 'label-head';

      const keySpan = textNode('span', field.key, 'test-key');
      const unitSpan = textNode('span', field.unit || '', 'test-unit');
      head.append(keySpan, unitSpan);

      const nameSpan = textNode('span', field.name, 'test-name');
      label.append(head, nameSpan);

      if (field.ref_range) {
        const refSpan = textNode('span', `Ref: ${field.ref_range}`, 'ref-pill');
        label.append(refSpan);
      }

      if (field.type === 'select') {
        const select = document.createElement('select');
        select.name = field.key;
        select.setAttribute('aria-label', field.name);

        const defaultOpt = document.createElement('option');
        defaultOpt.value = '';
        defaultOpt.textContent = 'Select...';
        select.append(defaultOpt);

        (field.options || []).forEach(opt => {
          const optEl = document.createElement('option');
          optEl.value = opt.value;
          optEl.textContent = opt.label;
          select.append(optEl);
        });
        label.append(select);
      } else {
        const input = document.createElement('input');
        input.name = field.key;
        input.type = 'number';
        input.step = field.step !== undefined ? field.step : 'any';
        if (field.min !== undefined) input.min = field.min;
        if (field.max !== undefined) input.max = field.max;
        input.placeholder = field.ref_range ? `e.g. ${field.ref_range.split(' ')[0]}` : 'Enter value';
        input.setAttribute('aria-label', field.name);
        label.append(input);
      }

      grid.append(label);
    });

    section.append(grid);
    container.append(section);
  });

  const form = el('prediction-form');
  form.oninput = onFormChange;
  form.onchange = onFormChange;
}

// 6. Form Value Getter and Tracker
function getFormValues() {
  const form = el('prediction-form');
  const data = {};
  if (!activeModule) return data;

  const fieldMap = {};
  activeModule.fields.forEach(f => { fieldMap[f.key] = f; });

  for (const input of form.querySelectorAll('input, select')) {
    if (!input.name) continue;
    const def = fieldMap[input.name] || {};
    const val = input.value.trim();

    if (val === '') {
      data[input.name] = null;
    } else if (def.type === 'select') {
      // Cast numeric option values if appropriate
      const numVal = Number(val);
      data[input.name] = isNaN(numVal) ? val : numVal;
    } else {
      const num = Number(val);
      data[input.name] = isNaN(num) ? null : num;
    }
  }
  return data;
}

function onFormChange() {
  revisionCounter++;
  el('error').hidden = true;
  el('result-status').textContent = 'Inputs modified';
}

// 7. Load Case Button Handler
el('load').onclick = () => {
  if (!activeModule || !activeModule.examples) return;
  const idx = el('example').value;
  const sample = activeModule.examples[idx];
  if (!sample || !sample.features) return;

  const form = el('prediction-form');
  for (const [key, value] of Object.entries(sample.features)) {
    const input = form.elements.namedItem(key);
    if (input) {
      input.value = value === null ? '' : value;
    }
  }
  onFormChange();
};

// 8. Form Submission (Prediction API)
el('prediction-form').onsubmit = async event => {
  event.preventDefault();
  if (!activeModule) return;

  const currentRevision = revisionCounter;
  const inputs = getFormValues();
  const submitBtn = el('submit');

  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span>Processing Panel...</span><span>⌛</span>';
  el('error').hidden = true;

  try {
    const response = await fetch(`/api/${activeModule.id}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(inputs)
    });

    const data = await response.json();
    if (currentRevision !== revisionCounter) return;

    if (!response.ok) {
      throw new Error(data.error || 'Failed to complete diagnostic inference.');
    }

    currentPrediction = { inputs, output: data };
    renderPredictionResult(data);
  } catch (err) {
    if (currentRevision === revisionCounter) {
      el('error').textContent = err.message;
      el('error').hidden = false;
      el('result-status').textContent = 'Input Error';
    }
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<span>Analyze Diagnostic Panel</span><span>→</span>';
  }
};

// 9. Render Prediction Outcome & Probability Breakdown
function renderPredictionResult(data) {
  el('empty-result').hidden = true;
  el('result').hidden = false;

  el('result-status').textContent = data.needs_review
    ? 'Review Required'
    : 'Analysis Complete';
  el('result-status').style.color = data.needs_review ? '#b45309' : '#087d79';

  el('target-label-overline').textContent = (data.target_label || 'PREDICTED STATUS').toUpperCase();
  el('prediction').textContent = data.prediction;
  el('top-score').textContent = `${(data.score * 100).toFixed(1)}%`;

  // Render Per-Class Probability Bars
  const barsContainer = el('score-bars');
  barsContainer.replaceChildren();

  const sortedScores = [...data.scores].sort((a, b) => b.score - a.score);
  sortedScores.forEach(s => {
    const item = document.createElement('div');
    item.className = 'score-item';

    const header = document.createElement('div');
    header.className = 'score-item-header';
    header.append(
      textNode('span', s.label),
      textNode('span', `${(s.score * 100).toFixed(1)}%`)
    );

    const track = document.createElement('div');
    track.className = 'bar-track';

    const fill = document.createElement('div');
    fill.className = 'bar-fill';
    fill.style.width = `${(s.score * 100).toFixed(1)}%`;
    track.append(fill);

    item.append(header, track);
    barsContainer.append(item);
  });

  // Clinical Quality & Imputation Notes
  const notesContainer = el('quality-notes');
  notesContainer.replaceChildren();
  notesContainer.append(textNode('p', data.note));

  if (data.missing && data.missing.length) {
    const imputedText = Object.entries(data.imputed_values)
      .map(([k, v]) => `${k} (${typeof v === 'number' ? v.toFixed(2) : v})`)
      .join(', ');
    notesContainer.append(
      textNode('p', `Training reference medians used for missing tests: ${imputedText}.`)
    );
  }

  if (data.out_of_range && data.out_of_range.length) {
    notesContainer.append(
      textNode('p', `Values outside observed clinical training ranges: ${data.out_of_range.join(', ')}. Interpretation confidence may vary.`)
    );
  }

  if (data.score < 0.65) {
    notesContainer.append(
      textNode('p', `Highest class probability is below 65%. Additional confirmatory testing recommended.`)
    );
  }

  // Explainability / Sensitivity Effects
  el('explanation-empty').hidden = true;
  el('explanation').hidden = false;
  const effectsContainer = el('effects');
  effectsContainer.replaceChildren();

  if (data.effects && data.effects.length) {
    data.effects.forEach(e => {
      const effectEl = document.createElement('div');
      effectEl.className = 'effect';

      const labelBox = document.createElement('div');
      const featName = textNode('strong', e.feature);
      const refVal = textNode(
        'small',
        `Population median reference: ${typeof e.reference === 'number' ? e.reference.toFixed(2) : e.reference}`
      );
      labelBox.append(featName, refVal);

      const deltaBadge = textNode(
        'span',
        `${e.effect_pp >= 0 ? '+' : ''}${e.effect_pp.toFixed(1)} pp`,
        'delta-badge'
      );
      deltaBadge.style.color = e.effect_pp >= 0 ? '#0f766e' : '#b45309';

      effectEl.append(labelBox, deltaBadge);
      effectsContainer.append(effectEl);
    });
  } else {
    effectsContainer.append(textNode('p', 'No sensitivity shifts observed.'));
  }

  showComparison();
}

// 10. Update Model Evaluation Charts and Metrics
function updateEvaluationSection(mod) {
  el('eval-section-title').textContent = `Model Evaluation: ${mod.test_name}`;
  el('eval-section-desc').textContent = `Validated on 20% held-out test partition with stratified 5-fold cross-validation on ${mod.metrics.samples} clinical records.`;

  const m = mod.metrics || {};
  el('metric-accuracy').innerHTML = `${(m.accuracy * 100).toFixed(1)}<small>%</small>`;
  el('metric-baseline').textContent = `Majority Baseline ${(m.baseline_accuracy * 100).toFixed(1)}%`;
  el('metric-f1').textContent = (m.macro_f1 || 0).toFixed(3);
  el('metric-balanced').innerHTML = `${(m.balanced_accuracy * 100).toFixed(1)}<small>%</small>`;
  el('metric-samples').textContent = m.test_samples || '--';

  const classCounts = m.class_counts
    ? Object.entries(m.class_counts).map(([k, v]) => `${k} (${v})`).join(' · ')
    : '';
  el('evaluation-note').textContent = `Class distributions in dataset: ${classCounts}.`;

  const timestamp = Date.now();
  el('chart-cm').src = `/artifacts/${mod.id}/confusion_matrix.png?v=${timestamp}`;
  el('chart-perf').src = `/artifacts/${mod.id}/class_performance.png?v=${timestamp}`;
  el('chart-imp').src = `/artifacts/${mod.id}/feature_importance.png?v=${timestamp}`;
}

// 11. Pin Comparison Logic
el('pin').onclick = () => {
  if (currentPrediction) {
    pinnedPrediction = structuredClone(currentPrediction);
    showComparison();
  }
};

function showComparison() {
  const box = el('comparison');
  box.replaceChildren();
  box.hidden = !pinnedPrediction;
  if (!pinnedPrediction) return;

  box.append(textNode('h3', `Pinned Reference: ${pinnedPrediction.output.prediction} (${(pinnedPrediction.output.score * 100).toFixed(1)}%)`));

  if (!currentPrediction) {
    box.append(textNode('p', 'Modify test panel parameters and re-analyze to compare relative shifts against this reference case.'));
    return;
  }

  const target = pinnedPrediction.output.prediction;
  const currentMatch = currentPrediction.output.scores.find(s => s.label === target);
  const afterScore = currentMatch ? currentMatch.score : 0;
  const delta = (afterScore - pinnedPrediction.output.score) * 100;

  const changedKeys = Object.keys(currentPrediction.inputs).filter(
    k => currentPrediction.inputs[k] !== pinnedPrediction.inputs[k]
  );

  box.append(
    textNode(
      'p',
      `Current Assessment: ${currentPrediction.output.prediction}. Likelihood for "${target}" shifted by ${delta >= 0 ? '+' : ''}${delta.toFixed(1)} percentage points.`
    )
  );

  box.append(
    textNode(
      'p',
      changedKeys.length
        ? `Modified biomarkers: ${changedKeys.join(', ')}.`
        : 'Identical biomarkers.'
    )
  );

  const clearBtn = textNode('button', 'Clear Pinned Reference', 'text-button');
  clearBtn.type = 'button';
  clearBtn.onclick = () => {
    pinnedPrediction = null;
    showComparison();
  };
  box.append(clearBtn);
}

// 12. JSON Export Handler
el('download').onclick = () => {
  if (!currentPrediction || !activeModule) return;
  const payload = {
    platform: 'DNA Clinical Diagnostic Intelligence',
    investigation: activeModule.test_name,
    timestamp: new Date().toISOString(),
    patient_inputs: currentPrediction.inputs,
    diagnostic_assessment: currentPrediction.output
  };

  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `DNA-${activeModule.id}-diagnostic-report.json`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};

// 13. Reset Handler
el('reset-button').onclick = () => {
  pinnedPrediction = null;
  setTimeout(() => {
    onFormChange();
    el('result').hidden = true;
    el('empty-result').hidden = false;
    el('explanation').hidden = true;
    el('explanation-empty').hidden = false;
    showComparison();
  }, 0);
};

// Start application
window.addEventListener('DOMContentLoaded', initApp);
