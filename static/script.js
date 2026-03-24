const state = {
    currentView: 'home', // home, dictation, answer, edit, settings
    books: [],
    currentBook: null,
    units: [],
    currentUnit: null,
    words: [],
    currentIndex: 0,
    timer: null,
    timeLeft: 10,
    isPaused: true,
    settings: {
        displayTime: 10
    }
};

// DOM Elements
const app = document.getElementById('app');
const content = document.getElementById('content');

// Init
async function init() {
    loadSettings();
    await fetchBooks();
    renderHome();
}

function loadSettings() {
    const saved = localStorage.getItem('dictationSettings');
    if (saved) {
        state.settings = JSON.parse(saved);
    }
}

async function fetchBooks() {
    const res = await fetch('/api/books');
    state.books = await res.json();
}

async function fetchUnits(bookId) {
    const res = await fetch(`/api/units/${bookId}`);
    state.units = await res.json();
}

async function fetchWords(unitId) {
    const res = await fetch(`/api/words/${unitId}`);
    state.words = await res.json();
}

// Rendering
function renderHome() {
    state.currentView = 'home';
    let html = `
        <div class="header">
            <h2>选择课程</h2>
            <a href="#" onclick="renderSettings()">设置</a>
        </div>
        <div class="book-list">
    `;
    
    if (state.books.length === 0) {
        html += '<p>暂无课本数据。</p>';
    } else {
        html += `
            <select id="book-select" onchange="handleBookSelect(this.value)">
                <option value="">请选择课本</option>
                ${state.books.map(b => `<option value="${b.id}" ${state.currentBook && state.currentBook.id == b.id ? 'selected' : ''}>${b.name}</option>`).join('')}
            </select>
        `;
    }

    html += '<div id="unit-list"></div></div>';
    content.innerHTML = html;
    
    if (state.currentBook) {
        renderUnitList();
    }
}

async function handleBookSelect(bookId) {
    if (!bookId) {
        state.currentBook = null;
        document.getElementById('unit-list').innerHTML = '';
        return;
    }
    state.currentBook = state.books.find(b => b.id == bookId);
    await fetchUnits(bookId);
    renderUnitList();
}

function renderUnitList() {
    const container = document.getElementById('unit-list');
    if (!state.units || state.units.length === 0) {
        container.innerHTML = '<p>该课本暂无单元。</p>';
        return;
    }
    
    container.innerHTML = state.units.map(u => `
        <div class="unit-item">
            <span>${u.name} (${u.word_count}词)</span>
            <div class="actions">
                <button class="btn-primary" onclick="startDictation(${u.id})">听写</button>
                <button class="btn-secondary" onclick="showAnswers(${u.id})">答案</button>
                <button class="btn-secondary" onclick="editUnit(${u.id})">编辑</button>
            </div>
        </div>
    `).join('');
}

// Navigation placeholders
async function startDictation(unitId) {
    state.currentUnit = state.units.find(u => u.id == unitId);
    await fetchWords(unitId);
    renderDictation();
}

async function showAnswers(unitId) {
    state.currentUnit = state.units.find(u => u.id == unitId);
    await fetchWords(unitId);
    renderAnswers();
}

async function editUnit(unitId) {
    state.currentUnit = state.units.find(u => u.id == unitId);
    await fetchWords(unitId);
    renderEdit();
}

function renderSettings() {
    state.currentView = 'settings';
    content.innerHTML = `
        <h2>设置</h2>
        <div class="form-group">
            <label>单词显示时间 (秒):</label>
            <input type="number" id="display-time" value="${state.settings.displayTime}" min="5" max="60">
        </div>
        <button class="btn-primary" onclick="saveSettings()">保存</button>
        <button class="btn-secondary" onclick="renderHome()">返回</button>
    `;
}

function saveSettings() {
    const time = parseInt(document.getElementById('display-time').value);
    if (time >= 5 && time <= 60) {
        state.settings.displayTime = time;
        localStorage.setItem('dictationSettings', JSON.stringify(state.settings));
        alert('设置已保存');
        renderHome();
    } else {
        alert('请输入5-60之间的数字');
    }
}

function renderDictation() {
    state.currentView = 'dictation';
    state.currentIndex = 0;
    state.isPaused = false;
    state.timeLeft = state.settings.displayTime || 10;
    
    updateDictationView();
    startTimer();
}

function updateDictationView() {
    if (state.currentIndex >= state.words.length) {
        finishDictation();
        return;
    }
    
    const word = state.words[state.currentIndex];
    let translationText = word.translation;
    if (word.pos) {
        translationText = `${word.pos} ${word.translation}`;
    } else if (word.type === 'phrase') {
        translationText = `phrase. ${word.translation}`;
    }
    
    content.innerHTML = `
        <div class="dictation-container">
            <div class="status-bar">
                <div class="progress">单词: ${state.currentIndex + 1} / ${state.words.length}</div>
                <div class="timer">倒计时: ${state.timeLeft}s</div>
            </div>
            <div class="word-card">
                ${translationText}
            </div>
            <div class="controls">
                <button class="btn-secondary" onclick="prevWord()" ${state.currentIndex === 0 ? 'disabled' : ''}>上一词</button>
                <button class="btn-primary" onclick="togglePause()">${state.isPaused ? '继续' : '暂停'}</button>
                <button class="btn-secondary" onclick="nextWord()">下一词</button>
            </div>
            <div style="margin-top: 20px; text-align: center;">
                 <button class="btn-secondary" onclick="stopDictation()">退出听写</button>
            </div>
        </div>
    `;
}

function startTimer() {
    stopTimer();
    state.timer = setInterval(() => {
        if (!state.isPaused) {
            state.timeLeft--;
            if (state.timeLeft <= 0) {
                playBeep();
                nextWord();
            } else {
                const timerEl = document.querySelector('.timer');
                if (timerEl) timerEl.innerText = `倒计时: ${state.timeLeft}s`;
            }
        }
    }, 1000);
}

function stopTimer() {
    if (state.timer) {
        clearInterval(state.timer);
        state.timer = null;
    }
}

function nextWord() {
    if (state.currentIndex < state.words.length - 1) {
        state.currentIndex++;
        state.timeLeft = state.settings.displayTime || 10;
        updateDictationView();
    } else {
        finishDictation();
    }
}

function prevWord() {
    if (state.currentIndex > 0) {
        state.currentIndex--;
        state.timeLeft = state.settings.displayTime || 10;
        updateDictationView();
    }
}

function togglePause() {
    state.isPaused = !state.isPaused;
    updateDictationView();
}

function playBeep() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.frequency.value = 880;
        gain.gain.value = 0.1;
        osc.start();
        setTimeout(() => osc.stop(), 500);
    } catch (e) {
        console.error('Audio play failed', e);
    }
}

function finishDictation() {
    stopTimer();
    content.innerHTML = `
        <div class="completion-screen" style="text-align: center; padding: 50px;">
            <h2>听写完成！</h2>
            <div style="margin-top: 20px;">
                <button class="btn-primary" onclick="renderAnswers()">查看答案</button>
                <button class="btn-secondary" onclick="renderHome()">返回选择</button>
            </div>
        </div>
    `;
}

function stopDictation() {
    stopTimer();
    renderHome();
}

function renderAnswers() {
    state.currentView = 'answer';
    const wordsHtml = state.words.map((w, i) => `
        <div class="answer-item">
            <span class="index">${i + 1}.</span>
            <span class="original"><strong>${w.original}</strong></span>
            <span class="translation">${w.pos ? w.pos + ' ' : ''}${w.translation}</span>
        </div>
    `).join('');
    
    content.innerHTML = `
        <h2>答案 - ${state.currentUnit.name}</h2>
        <div class="answer-grid">
            ${wordsHtml}
        </div>
        <div style="margin-top: 20px; text-align: center;">
            <button class="btn-secondary" onclick="renderHome()">返回</button>
        </div>
    `;
}

function renderEdit() {
    state.currentView = 'edit';
    const rows = state.words.map((w, i) => `
        <tr data-id="${w.id}">
            <td>${i + 1}</td>
            <td><input type="text" value="${w.original}" class="edit-original"></td>
            <td><input type="text" value="${w.translation}" class="edit-translation"></td>
            <td><input type="text" value="${w.pos || ''}" class="edit-pos"></td>
            <td>
                <button class="btn-primary" onclick="saveWord(${w.id}, this)">保存</button>
                <button class="btn-secondary" onclick="deleteWord(${w.id})">删除</button>
            </td>
        </tr>
    `).join('');
    
    content.innerHTML = `
        <h2>编辑 - ${state.currentUnit.name}</h2>
        <table class="edit-table" style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr>
                    <th>序号</th>
                    <th>原文</th>
                    <th>翻译</th>
                    <th>词性</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                ${rows}
                <tr class="add-row">
                    <td>+</td>
                    <td><input type="text" id="new-original" placeholder="新单词"></td>
                    <td><input type="text" id="new-translation" placeholder="翻译"></td>
                    <td><input type="text" id="new-pos" placeholder="词性"></td>
                    <td><button class="btn-primary" onclick="addWord()">添加</button></td>
                </tr>
            </tbody>
        </table>
        <div style="margin-top: 20px; text-align: center;">
            <button class="btn-secondary" onclick="renderHome()">返回</button>
        </div>
    `;
}

async function saveWord(id, btn) {
    const row = btn.closest('tr');
    const original = row.querySelector('.edit-original').value;
    const translation = row.querySelector('.edit-translation').value;
    const pos = row.querySelector('.edit-pos').value;
    
    const res = await fetch(`/api/words/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ original, translation, pos })
    });
    
    if (res.ok) {
        alert('保存成功');
        await fetchWords(state.currentUnit.id); // Refresh data
    } else {
        alert('保存失败');
    }
}

async function deleteWord(id) {
    if (!confirm('确定删除吗？')) return;
    
    const res = await fetch(`/api/words/${id}`, {
        method: 'DELETE'
    });
    
    if (res.ok) {
        await fetchWords(state.currentUnit.id);
        renderEdit();
    } else {
        alert('删除失败');
    }
}

async function addWord() {
    const original = document.getElementById('new-original').value;
    const translation = document.getElementById('new-translation').value;
    const pos = document.getElementById('new-pos').value;
    
    if (!original || !translation) {
        alert('原文和翻译必填');
        return;
    }
    
    const res = await fetch('/api/words', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ 
            unit_id: state.currentUnit.id,
            original, 
            translation, 
            pos,
            type: original.includes(' ') ? 'phrase' : 'word' // Simple auto-detect
        })
    });
    
    if (res.ok) {
        await fetchWords(state.currentUnit.id);
        renderEdit();
    } else {
        alert('添加失败');
    }
}

// Start
init();
