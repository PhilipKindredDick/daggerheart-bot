/**
 * Интеграция с Telegram Web App API
 */

class TelegramWebApp {
    constructor() {
        this.tg = null;
        this.user = null;
        this.initialized = false;
        this.init();
    }

    init() {
        try {
            // Проверяем доступность Telegram WebApp
            if (!window.Telegram || !window.Telegram.WebApp) {
                console.error('Telegram WebApp не доступен');
                this.showError('Telegram WebApp не доступен');
                return;
            }

            this.tg = window.Telegram.WebApp;
            
            // Инициализация Telegram Web App
            this.tg.ready();
            
            // Настройка темы
            this.setupTheme();
            
            // Получение данных пользователя
            this.getUserData();
            
            // Настройка главной кнопки
            this.setupMainButton();
            
            // Настройка кнопки "Назад"
            this.setupBackButton();
            
            // Включение закрытия по подтверждению
            this.tg.enableClosingConfirmation();
            
            this.initialized = true;
            console.log('Telegram Web App initialized successfully');
            
        } catch (error) {
            console.error('Ошибка инициализации Telegram WebApp:', error);
            this.showError('Ошибка инициализации: ' + error.message);
        }
    }

    showError(message) {
        const errorScreen = document.getElementById('error-screen');
        const errorMessage = document.getElementById('error-message');
        const loadingScreen = document.getElementById('loading-screen');
        
        if (errorScreen && errorMessage) {
            errorMessage.textContent = message;
            errorScreen.classList.add('active');
            if (loadingScreen) {
                loadingScreen.classList.remove('active');
            }
        }
    }

    setupTheme() {
        try {
            // Применяем цвета темы Telegram
            const themeParams = this.tg.themeParams;
            
            if (themeParams && themeParams.bg_color) {
                document.body.style.backgroundColor = themeParams.bg_color;
            }
            
            if (themeParams && themeParams.text_color) {
                document.body.style.color = themeParams.text_color;
            }
            
            // Уведомляем Telegram о готовности
            this.tg.expand();
        } catch (error) {
            console.error('Ошибка настройки темы:', error);
        }
    }

    getUserData() {
        this.user = this.tg.initDataUnsafe?.user;
        
        if (this.user) {
            const username = this.user.first_name || this.user.username || 'Искатель приключений';
            const usernameElement = document.getElementById('username');
            if (usernameElement) {
                usernameElement.textContent = `Привет, ${username}!`;
            }
            
            console.log('User data:', this.user);
        }
    }

    setupMainButton() {
        this.tg.MainButton.setText('Продолжить');
        this.tg.MainButton.hide();
        
        this.tg.MainButton.onClick(() => {
            console.log('Main button clicked');
            this.onMainButtonClick();
        });
    }

    setupBackButton() {
        this.tg.BackButton.onClick(() => {
            console.log('Back button clicked');
            this.onBackButtonClick();
        });
    }

    showMainButton(text = 'Продолжить', callback = null) {
        this.tg.MainButton.setText(text);
        this.tg.MainButton.show();
        
        if (callback) {
            this.mainButtonCallback = callback;
        }
    }

    hideMainButton() {
        this.tg.MainButton.hide();
        this.mainButtonCallback = null;
    }

    showBackButton() {
        this.tg.BackButton.show();
    }

    hideBackButton() {
        this.tg.BackButton.hide();
    }

    onMainButtonClick() {
        if (this.mainButtonCallback) {
            this.mainButtonCallback();
        }
    }

    onBackButtonClick() {
        // Возвращаемся к предыдущему экрану
        window.gameApp.goBack();
    }

    sendData(data) {
        // Отправляем данные боту
        this.tg.sendData(JSON.stringify(data));
    }

    showAlert(message) {
        this.tg.showAlert(message);
    }

    showConfirm(message, callback) {
        this.tg.showConfirm(message, callback);
    }

    showPopup(params) {
        this.tg.showPopup(params);
    }

    hapticFeedback(type = 'light') {
        // Типы: light, medium, heavy, rigid, soft
        this.tg.HapticFeedback.impactOccurred(type);
    }

    notificationFeedback(type = 'success') {
        // Типы: error, success, warning
        this.tg.HapticFeedback.notificationOccurred(type);
    }

    selectionFeedback() {
        this.tg.HapticFeedback.selectionChanged();
    }

    close() {
        this.tg.close();
    }

    getUserId() {
        return this.user?.id || null;
    }

    getUsername() {
        return this.user?.username || null;
    }

    getFirstName() {
        return this.user?.first_name || null;
    }

    getLanguageCode() {
        return this.user?.language_code || 'ru';
    }

    isExpanded() {
        return this.tg.isExpanded;
    }

    getViewportHeight() {
        return this.tg.viewportHeight;
    }

    getViewportStableHeight() {
        return this.tg.viewportStableHeight;
    }

    getHeaderColor() {
        return this.tg.headerColor;
    }

    getBackgroundColor() {
        return this.tg.backgroundColor;
    }

    setHeaderColor(color) {
        this.tg.setHeaderColor(color);
    }

    setBackgroundColor(color) {
        this.tg.setBackgroundColor(color);
    }
}

// Создаем глобальный экземпляр
window.telegramApp = new TelegramWebApp();