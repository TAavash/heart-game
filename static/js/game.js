document.addEventListener('DOMContentLoaded', function () {
    const timerElement = document.getElementById('timer').querySelector('strong');
    const gameForm = document.getElementById('game-form');
    const guessInput = document.getElementById('guess');
    const answerButtons = document.querySelectorAll('.answer-btn');

    let timeLeft = 15;
    let timerInterval;

    function startTimer() {
        timerInterval = setInterval(() => {
            timeLeft--;
            timerElement.textContent = timeLeft;

            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                window.location.href = '/game_over';
            }
        }, 1000);
    }

    answerButtons.forEach(button => {
        button.addEventListener('click', function () {
            guessInput.value = this.dataset.value;
            gameForm.submit();
        });
    });

    startTimer();
});
