// 表单验证函数
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const inputs = form.querySelectorAll('input[required], select[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('error');
        } else {
            input.classList.remove('error');
        }
    });

    return isValid;
}

// 动态加载服装列表
async function loadClothingList() {
    try {
        const response = await fetch('/api/clothing');
        const data = await response.json();
        
        const select = document.getElementById('clothing_id');
        if (select) {
            select.innerHTML = '<option value="">请选择服装</option>';
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.textContent = `${item.name} - ${item.category} - ${item.size} - ${item.color}`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载服装列表失败:', error);
    }
}

// 查询表单动态显示/隐藏
function toggleSearchValue() {
    const searchType = document.getElementById('search_type');
    const searchValueGroup = document.getElementById('search_value_group');
    
    if (searchType && searchValueGroup) {
        if (searchType.value === 'all') {
            searchValueGroup.style.display = 'none';
        } else {
            searchValueGroup.style.display = 'block';
        }
    }
}

// 表单验证功能
function validateAddClothingForm() {
    const form = document.getElementById('addClothingForm');
    const clothingId = document.getElementById('clothing_id');
    const costPrice = document.getElementById('cost_price');
    const retailPrice = document.getElementById('retail_price');
    
    // 重置之前的验证状态
    form.classList.remove('was-validated');
    
    let isValid = true;
    
    // 验证服装编号（不能为空且长度至少为3个字符）
    if (!clothingId.value || clothingId.value.length < 3) {
        clothingId.classList.add('is-invalid');
        isValid = false;
    }
    
    // 验证价格
    if (costPrice.value <= 0) {
        costPrice.classList.add('is-invalid');
        isValid = false;
    }
    
    if (retailPrice.value <= 0) {
        retailPrice.classList.add('is-invalid');
        isValid = false;
    }
    
    // 验证零售价必须大于成本价
    if (parseFloat(retailPrice.value) <= parseFloat(costPrice.value)) {
        retailPrice.classList.add('is-invalid');
        retailPrice.nextElementSibling.textContent = '零售价必须大于成本价';
        isValid = false;
    }
    
    // 如果验证通过，添加验证样式
    if (isValid) {
        form.classList.add('was-validated');
    }
    
    return isValid;
}

function validateUpdateClothingForm() {
    const form = document.getElementById('updateClothingForm');
    const costPrice = document.getElementById('cost_price');
    const retailPrice = document.getElementById('retail_price');
    
    // 重置之前的验证状态
    form.classList.remove('was-validated');
    
    let isValid = true;
    
    // 验证价格
    if (costPrice.value <= 0) {
        costPrice.classList.add('is-invalid');
        isValid = false;
    }
    
    if (retailPrice.value <= 0) {
        retailPrice.classList.add('is-invalid');
        isValid = false;
    }
    
    // 验证零售价必须大于成本价
    if (parseFloat(retailPrice.value) <= parseFloat(costPrice.value)) {
        retailPrice.classList.add('is-invalid');
        retailPrice.nextElementSibling.textContent = '零售价必须大于成本价';
        isValid = false;
    }
    
    // 如果验证通过，添加验证样式
    if (isValid) {
        form.classList.add('was-validated');
    }
    
    return isValid;
}

// 实时价格验证
function setupPriceValidation() {
    const costPrice = document.getElementById('cost_price');
    const retailPrice = document.getElementById('retail_price');
    
    if (costPrice && retailPrice) {
        costPrice.addEventListener('input', function() {
            if (parseFloat(retailPrice.value) <= parseFloat(this.value)) {
                retailPrice.classList.add('is-invalid');
                retailPrice.nextElementSibling.textContent = '零售价必须大于成本价';
            } else {
                retailPrice.classList.remove('is-invalid');
            }
        });
        
        retailPrice.addEventListener('input', function() {
            if (parseFloat(this.value) <= parseFloat(costPrice.value)) {
                this.classList.add('is-invalid');
                this.nextElementSibling.textContent = '零售价必须大于成本价';
            } else {
                this.classList.remove('is-invalid');
            }
        });
    }
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 为所有表单添加验证
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form.id)) {
                e.preventDefault();
                alert('请填写所有必填字段');
            }
        });
    });

    // 加载服装列表
    if (document.getElementById('clothing_id')) {
        loadClothingList();
    }

    // 监听查询类型变化
    const searchType = document.getElementById('search_type');
    if (searchType) {
        searchType.addEventListener('change', toggleSearchValue);
        toggleSearchValue(); // 初始化显示状态
    }

    setupPriceValidation();
}); 