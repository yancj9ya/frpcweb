document.addEventListener('DOMContentLoaded', () => {
    // 移动端导航菜单
    const mobileMenu = document.getElementById('mobile-menu');
    const navLinks = document.querySelector('.nav-links');

    // 添加代理弹窗
    const addModal = document.getElementById('add-proxy-modal');
    const openAddModal = document.getElementById('open-add-modal');
    const closeAddModal = document.getElementById('close-add-modal');
    const cancelAddModal = document.getElementById('cancel-add-modal');

    const closeModal = () => {
        if (!addModal) return;
        addModal.classList.remove('is-open');
        addModal.setAttribute('aria-hidden', 'true');
    };

    const openModal = () => {
        if (!addModal) return;
        addModal.classList.add('is-open');
        addModal.setAttribute('aria-hidden', 'false');
    };

    if (openAddModal) {
        openAddModal.addEventListener('click', openModal);
    }

    if (closeAddModal) {
        closeAddModal.addEventListener('click', closeModal);
    }

    if (cancelAddModal) {
        cancelAddModal.addEventListener('click', closeModal);
    }

    if (addModal) {
        addModal.addEventListener('click', (event) => {
            if (event.target === addModal) {
                closeModal();
            }
        });
    }

    // 代理列表筛选
    const filterChips = document.querySelectorAll('.filter-chip');
    const proxyList = document.getElementById('proxy-list');
    if (filterChips.length && proxyList) {
        const applyFilters = () => {
            const activeFilters = Array.from(filterChips)
                .filter(chip => chip.classList.contains('is-active'))
                .map(chip => chip.dataset.filter);

            const items = proxyList.querySelectorAll('.proxy-item');
            items.forEach(item => {
                const types = (item.dataset.types || '').trim().split(/\s+/).filter(Boolean);
                const groupVisible = item.dataset.visible === 'true';

                const matchesAll = activeFilters.every(filter => {
                    if (filter === 'all') {
                        return true;
                    }
                    if (filter === 'tcp' || filter === 'udp') {
                        return types.includes(filter);
                    }
                    if (filter === 'visible') {
                        return groupVisible;
                    }
                    if (filter === 'hidden') {
                        return !groupVisible;
                    }
                    return true;
                });

                item.style.display = matchesAll ? '' : 'none';
            });
        };

        filterChips.forEach(chip => {
            chip.addEventListener('click', () => {
                if (chip.dataset.filter === 'all') {
                    const isActive = chip.classList.contains('is-active');
                    filterChips.forEach(other => other.classList.remove('is-active'));
                    if (!isActive) {
                        chip.classList.add('is-active');
                    }
                } else {
                    chip.classList.toggle('is-active');
                    const allChip = document.querySelector('.filter-chip[data-filter="all"]');
                    if (allChip) {
                        allChip.classList.remove('is-active');
                    }
                }
                applyFilters();
            });
        });

        applyFilters();
    }

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
