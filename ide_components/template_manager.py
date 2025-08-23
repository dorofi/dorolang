class TemplateManager:
    """Менеджер шаблонов кода"""
    
    @staticmethod
    def get_templates():
        """Возвращает словарь доступных шаблонов"""
        return {
            "Hello World": '''# Hello World на DoroLang
say "Hello, DoroLang!"
say "Добро пожаловать в мир программирования!"''',
            
            "Variables": '''# Работа с переменными
kas name = "Ваше имя"
kas age = 25
kas is_student = true

say "Имя: " + name
say "Возраст: " + age
say "Студент: " + is_student''',
            
            "Conditional Logic": '''# Условная логика
kas score = 85
kas passed = score >= 60

if (passed) {
    say "Поздравляем! Вы прошли тест!"
    kas grade = "Зачёт"
} else {
    say "К сожалению, тест не пройден"
    kas grade = "Незачёт"
}

say "Итоговая оценка: " + grade''',
            
            "Complex Logic": '''# Сложная логика
kas temperature = 22
kas is_sunny = true
kas is_weekend = false

kas good_weather = temperature > 20 and is_sunny
kas can_go_out = good_weather and (is_weekend or temperature > 25)

if (can_go_out) {
    say "Отличная погода для прогулки!"
} else {
    if (not good_weather) {
        say "Погода не очень хорошая"
    } else {
        say "Погода хорошая, но сегодня рабочий день"
    }
}''',
            
            "Calculator": '''# Простой калькулятор
kas a = 15
kas b = 7

say "Число A: " + a
say "Число B: " + b
say "Сумма: " + (a + b)
say "Разность: " + (a - b)
say "Произведение: " + (a * b)
say "Частное: " + (a / b)
say "Остаток: " + (a % b)

# Сравнения
say "A больше B: " + (a > b)
say "A равно B: " + (a == b)
say "A не равно B: " + (a != b)'''
        }

