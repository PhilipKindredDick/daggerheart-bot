/**
 * Основная логика приложения Daggerheart
 */

class GameApp {
    constructor() {
        this.currentScreen = 'loading-screen';
        this.gameState = {
            character: null,
            hope: 5,
            fear: 3,
            isGameActive: false
        };
        this.screenHistory = [];
        this.apiUrl = 'http://localhost:8000/api';
        
        this.init();
    }

    init() {
        console.log('GameApp initialized');
        
        // Имитируем загрузку
        setTimeout(() => {
            this.showScreen('main-menu');
        }, 2000);
        
        // Настраиваем обработчики форм
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Форма создания персонажа
        const characterForm = document.getElementById('character-form');
        if (characterForm) {
            characterForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createCharacter();
            });
        }

        // Обработчики кнопок действий
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-action')) {
                window.telegramApp.hapticFeedback('light');
            }
        });
    }

    showScreen(screenId) {
        // Скрываем все экраны
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        // Показываем нужный экран
        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.classList.add('active');
            this.screenHistory.push(this.currentScreen);
            this.currentScreen = screenId;
            
            // Управляем кнопками Telegram
            this.updateTelegramButtons();
        }
    }

    updateTelegramButtons() {
        switch (this.currentScreen) {
            case 'main-menu':
                window.telegramApp.hideMainButton();
                window.telegramApp.hideBackButton();
                break;
            case 'character-creation':
                window.telegramApp.hideMainButton();
                window.telegramApp.showBackButton();
                break;
            case 'game-screen':
                window.telegramApp.hideMainButton();
                window.telegramApp.showBackButton();
                break;
            default:
                window.telegramApp.hideMainButton();
                window.telegramApp.hideBackButton();
        }
    }

    goBack() {
        if (this.screenHistory.length > 0) {
            const previousScreen = this.screenHistory.pop();
            this.showScreen(previousScreen);
        } else {
            this.showScreen('main-menu');
        }
    }

    // Функции для кнопок главного меню
    startNewGame() {
        window.telegramApp.hapticFeedback('medium');
        this.showScreen('character-creation');
    }

    loadGame() {
        window.telegramApp.hapticFeedback('light');
        window.telegramApp.showAlert('Загрузка игры пока не реализована');
    }

    showCharacter() {
        window.telegramApp.hapticFeedback('light');
        if (this.gameState.character) {
            this.displayCharacterInfo();
        } else {
            window.telegramApp.showAlert('Сначала создайте персонажа');
        }
    }

    showRules() {
        window.telegramApp.hapticFeedback('light');
        window.telegramApp.showAlert('Правила игры можно найти на сайте daggerheart.su');
    }

    showMainMenu() {
        window.telegramApp.hapticFeedback('light');
        this.showScreen('main-menu');
    }

    // Создание персонажа
    async createCharacter() {
        const name = document.getElementById('character-name').value.trim();
        const characterClass = document.getElementById('character-class').value;
        const ancestry = document.getElementById('character-ancestry').value;

        if (!name || !characterClass || !ancestry) {
            window.telegramApp.showAlert('Заполните все поля');
            return;
        }

        window.telegramApp.hapticFeedback('medium');
        
        try {
            const characterData = {
                name,
                class: characterClass,
                ancestry,
                userId: window.telegramApp.getUserId()
            };

            // Отправляем данные на сервер
            const response = await this.apiRequest('POST', '/character', characterData);
            
            if (response.success) {
                this.gameState.character = response.character;
                window.telegramApp.notificationFeedback('success');
                this.showScreen('game-screen');
                this.startGameSession();
            } else {
                throw new Error(response.message || 'Ошибка создания персонажа');
            }
        } catch (error) {
            console.error('Error creating character:', error);
            window.telegramApp.notificationFeedback('error');
            window.telegramApp.showAlert('Ошибка создания персонажа: ' + error.message);
        }
    }

    // Запуск игровой сессии
    async startGameSession() {
        try {
            const response = await this.apiRequest('POST', '/game/start', {
                characterId: this.gameState.character.id,
                userId: window.telegramApp.getUserId()
            });

            if (response.success) {
                this.gameState.isGameActive = true;
                this.updateStoryText(response.narrative);
                this.updateCharacterStatus();
            }
        } catch (error) {
            console.error('Error starting game session:', error);
            window.telegramApp.showAlert('Ошибка запуска игры: ' + error.message);
        }
    }

    // Игровые действия
    async rollDice() {
        if (!this.gameState.isGameActive) {
            window.telegramApp.showAlert('Сначала начните игру');
            return;
        }

        window.telegramApp.hapticFeedback('heavy');
        
        try {
            const response = await this.apiRequest('POST', '/game/roll-dice', {
                characterId: this.gameState.character.id,
                userId: window.telegramApp.getUserId()
            });

            if (response.success) {
                this.updateStoryText(response.narrative);
                this.updateCharacterStatus(response.character);
                window.telegramApp.notificationFeedback('success');
            }
        } catch (error) {
            console.error('Error rolling dice:', error);
            window.telegramApp.showAlert('Ошибка броска костей: ' + error.message);
        }
    }

    async useAbility() {
        if (!this.gameState.isGameActive) {
            window.telegramApp.showAlert('Сначала начните игру');
            return;
        }

        window.telegramApp.hapticFeedback('medium');
        window.telegramApp.showAlert('Выбор способностей пока в разработке');
    }

    async interact() {
        if (!this.gameState.isGameActive) {
            window.telegramApp.showAlert('Сначала начните игру');
            return;
        }

        window.telegramApp.hapticFeedback('light');
        window.telegramApp.showAlert('Взаимодействие пока в разработке');
    }

    // Обновление интерфейса
    updateStoryText(text) {
        const storyElement = document.getElementById('story-text');
        if (storyElement && text) {
            const newParagraph = document.createElement('p');
            newParagraph.textContent = text;
            storyElement.appendChild(newParagraph);
            
            // Прокручиваем вниз
            storyElement.scrollTop = storyElement.scrollHeight;
        }
    }

    updateCharacterStatus(character = null) {
        const char = character || this.gameState.character;
        if (!char) return;

        // Обновляем Hope
        const hopeBar = document.getElementById('hope-bar');
        const hopeValue = document.getElementById('hope-value');
        if (hopeBar && hopeValue) {
            const hopePercent = (char.hope / 10) * 100;
            hopeBar.style.width = hopePercent + '%';
            hopeValue.textContent = char.hope;
        }

        // Обновляем Fear
        const fearBar = document.getElementById('fear-bar');
        const fearValue = document.getElementById('fear-value');
        if (fearBar && fearValue) {
            const fearPercent = (char.fear / 10) * 100;
            fearBar.style.width = fearPercent + '%';
            fearValue.textContent = char.fear;
        }

        this.gameState.hope = char.hope;
        this.gameState.fear = char.fear;
    }

    displayCharacterInfo() {
        const char = this.gameState.character;
        const info = `
Имя: ${char.name}
Класс: ${char.class}
Происхождение: ${char.ancestry}
Hope: ${char.hope}
Fear: ${char.fear}
        `;
        
        window.telegramApp.showAlert(info);
    }

    // API запросы
    async apiRequest(method, endpoint, data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(this.apiUrl + endpoint, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }
}

// Глобальные функции для кнопок
function startNewGame() {
    window.gameApp.startNewGame();
}

function loadGame() {
    window.gameApp.loadGame();
}

function showCharacter() {
    window.gameApp.showCharacter();
}

function showRules() {
    window.gameApp.showRules();
}

function showMainMenu() {
    window.gameApp.showMainMenu();
}

function rollDice() {
    window.gameApp.rollDice();
}

function useAbility() {
    window.gameApp.useAbility();
}

function interact() {
    window.gameApp.interact();
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    window.gameApp = new GameApp();
});

// Обработка события закрытия
window.addEventListener('beforeunload', () => {
    // Сохраняем состояние игры если нужно
    console.log('App is closing');
});