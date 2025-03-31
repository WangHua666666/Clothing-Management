/**
 * 表单验证函数 - 验证指定表单的必填字段
 * @param {string} formId - 需要验证的表单ID
 * @returns {boolean} - 返回验证结果，true表示验证通过，false表示验证失败
 */
function validateForm(formId) {
    // 获取表单DOM元素
    const form = document.getElementById(formId);
    if (!form) return true; // 如果表单不存在，返回true避免阻止提交

    // 获取表单中所有带required属性的输入和选择元素
    const inputs = form.querySelectorAll('input[required], select[required]');
    let isValid = true;

    // 遍历每个必填字段进行验证
    inputs.forEach(input => {
        if (!input.value.trim()) {
            // 如果字段为空，标记为无效并添加错误样式
            isValid = false;
            input.classList.add('error');
        } else {
            // 如果字段有值，移除错误样式
            input.classList.remove('error');
        }
    });

    return isValid; // 返回整体验证结果
}

/**
 * 动态加载服装列表 - 从API获取服装数据并填充到选择框中
 * @async
 * @returns {Promise<void>} - 无返回值
 */
async function loadClothingList() {
    try {
        // 从API获取服装数据
        const response = await fetch('/api/clothing');
        const data = await response.json();
        
        // 获取要填充的选择框元素
        const select = document.getElementById('clothing_id');
        if (select) {
            // 清空现有选项并添加默认选项
            select.innerHTML = '<option value="">请选择服装</option>';
            // 遍历服装数据，为每个服装创建选项
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.textContent = `${item.name} - ${item.category} - ${item.size} - ${item.color}`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        // 记录错误信息，但不中断用户操作
        console.error('加载服装列表失败:', error);
    }
}

/**
 * 查询表单组件动态显示/隐藏控制 - 根据查询类型控制搜索值输入框的显示状态
 * @returns {void} - 无返回值
 */
function toggleSearchValue() {
    // 获取查询类型和搜索值组元素
    const searchType = document.getElementById('search_type');
    const searchValueGroup = document.getElementById('search_value_group');
    
    if (searchType && searchValueGroup) {
        // 如果查询类型为"全部"，则隐藏搜索值输入框
        if (searchType.value === 'all') {
            searchValueGroup.style.display = 'none';
        } else {
            // 否则显示搜索值输入框
            searchValueGroup.style.display = 'block';
        }
    }
}

/**
 * 服装添加表单验证 - 验证服装添加表单的完整性和逻辑
 * @returns {boolean} - 返回验证结果，true表示验证通过，false表示验证失败
 */
function validateAddClothingForm() {
    // 获取表单和关键字段元素
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
    
    // 验证成本价 - 必须大于0
    if (costPrice.value <= 0) {
        costPrice.classList.add('is-invalid');
        isValid = false;
    }
    
    // 验证零售价 - 必须大于0
    if (retailPrice.value <= 0) {
        retailPrice.classList.add('is-invalid');
        isValid = false;
    }
    
    // 验证零售价必须大于成本价 - 业务逻辑验证
    if (parseFloat(retailPrice.value) <= parseFloat(costPrice.value)) {
        retailPrice.classList.add('is-invalid');
        retailPrice.nextElementSibling.textContent = '零售价必须大于成本价';
        isValid = false;
    }
    
    // 如果验证通过，添加Bootstrap验证样式
    if (isValid) {
        form.classList.add('was-validated');
    }
    
    return isValid; // 返回整体验证结果
}

/**
 * 服装更新表单验证 - 验证服装更新表单的完整性和逻辑
 * @returns {boolean} - 返回验证结果，true表示验证通过，false表示验证失败
 */
function validateUpdateClothingForm() {
    // 获取表单和关键字段元素
    const form = document.getElementById('updateClothingForm');
    const costPrice = document.getElementById('cost_price');
    const retailPrice = document.getElementById('retail_price');
    
    // 重置之前的验证状态
    form.classList.remove('was-validated');
    
    let isValid = true;
    
    // 验证成本价 - 必须大于0
    if (costPrice.value <= 0) {
        costPrice.classList.add('is-invalid');
        isValid = false;
    }
    
    // 验证零售价 - 必须大于0
    if (retailPrice.value <= 0) {
        retailPrice.classList.add('is-invalid');
        isValid = false;
    }
    
    // 验证零售价必须大于成本价 - 业务逻辑验证
    if (parseFloat(retailPrice.value) <= parseFloat(costPrice.value)) {
        retailPrice.classList.add('is-invalid');
        retailPrice.nextElementSibling.textContent = '零售价必须大于成本价';
        isValid = false;
    }
    
    // 如果验证通过，添加Bootstrap验证样式
    if (isValid) {
        form.classList.add('was-validated');
    }
    
    return isValid; // 返回整体验证结果
}

/**
 * 设置价格实时验证 - 为价格输入框添加实时验证事件监听器
 * @returns {void} - 无返回值
 */
function setupPriceValidation() {
    // 获取成本价和零售价输入框元素
    const costPrice = document.getElementById('cost_price');
    const retailPrice = document.getElementById('retail_price');
    
    if (costPrice && retailPrice) {
        // 为成本价添加输入事件监听器
        costPrice.addEventListener('input', function() {
            // 当成本价变化时，验证成本价和零售价的关系
            if (parseFloat(retailPrice.value) <= parseFloat(this.value)) {
                retailPrice.classList.add('is-invalid');
                retailPrice.nextElementSibling.textContent = '零售价必须大于成本价';
            } else {
                retailPrice.classList.remove('is-invalid');
            }
        });
        
        // 为零售价添加输入事件监听器
        retailPrice.addEventListener('input', function() {
            // 当零售价变化时，验证成本价和零售价的关系
            if (parseFloat(this.value) <= parseFloat(costPrice.value)) {
                this.classList.add('is-invalid');
                this.nextElementSibling.textContent = '零售价必须大于成本价';
            } else {
                this.classList.remove('is-invalid');
            }
        });
    }
}

// DOM内容加载完成后执行初始化函数
document.addEventListener('DOMContentLoaded', function() {
    // 为所有表单添加提交验证
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // 如果表单验证失败，阻止提交并显示提示
            if (!validateForm(form.id)) {
                e.preventDefault();
                alert('请填写所有必填字段');
            }
        });
    });

    // 如果存在服装ID选择框，加载服装列表
    if (document.getElementById('clothing_id')) {
        loadClothingList();
    }

    // 设置查询类型变化监听
    const searchType = document.getElementById('search_type');
    if (searchType) {
        searchType.addEventListener('change', toggleSearchValue);
        toggleSearchValue(); // 初始化显示状态
    }

    // 设置价格实时验证
    setupPriceValidation();
}); 