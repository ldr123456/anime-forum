// 二次元交流站 - 前端交互

// 颜色选择器联动
document.addEventListener('DOMContentLoaded', function() {
    const colorInput = document.querySelector('input[type="color"]');
    const colorText = document.getElementById('themeColorText');
    if (colorInput && colorText) {
        colorInput.addEventListener('input', function() {
            colorText.value = this.value;
        });
    }

    // 自动隐藏 flash 消息
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 4000);
    });
});

// 随机颜色
function randomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    document.querySelector('input[type="color"]').value = color;
    document.getElementById('themeColorText').value = color;
}
