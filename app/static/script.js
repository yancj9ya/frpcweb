document.addEventListener('DOMContentLoaded', () => {
    // 移动端导航菜单
    const mobileMenu = document.getElementById('mobile-menu');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenu && navLinks) {
        mobileMenu.addEventListener('click', function () {
            navLinks.classList.toggle('open');

            const spans = mobileMenu.querySelectorAll('span');
            if (navLinks.classList.contains('open')) {
                spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(-45deg) translate(6px, -6px)';
            } else {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        });

        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('open');
                const spans = mobileMenu.querySelectorAll('span');
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            });
        });
    }

    // 删除确认对话框
    const deleteLinks = document.querySelectorAll('a.secondary.warning');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('确定要删除这个代理吗？此操作无法撤销')) {
                e.preventDefault();
            }
        });
    });
    
    // 表单提交动画
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.innerHTML = '保存中...';
                submitButton.disabled = true;
                submitButton.classList.add('processing');
            }
        });
    });
    
    // 添加淡入动画到所有卡片
    const cards = document.querySelectorAll('.card, .proxy-card');
    cards.forEach((card, index) => {
        // 添加fade-in类以触发动画
        card.classList.add('fade-in');
        card.style.animationDelay = `${index * 0.05}s`;
    });
    
    // 输入框焦点效果
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        // 只对表单内的输入框添加焦点效果
        if (input.closest('form')) {
            input.addEventListener('focus', function() {
                this.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.classList.remove('focused');
            });
        }
    });
    
    // 为所有按钮添加悬停音效（视觉反馈）
    const buttons = document.querySelectorAll('button, a[role="button"]');
    buttons.forEach(button => {
        button.addEventListener('mousedown', function() {
            this.classList.add('active');
        });
        
        button.addEventListener('mouseup', function() {
            this.classList.remove('active');
        });
        
        button.addEventListener('mouseleave', function() {
            this.classList.remove('active');
        });
    });
});
