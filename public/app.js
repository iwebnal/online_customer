// Telegram Mini App frontend for cafe menu
// Compatible script (no modules, no optional chaining)

(function () {
  // --- Lightweight polyfills for older iOS WebKit ---
  if (typeof NodeList !== 'undefined' && !NodeList.prototype.forEach) {
    NodeList.prototype.forEach = function (cb, thisArg) {
      for (var i = 0; i < this.length; i++) cb.call(thisArg, this[i], i, this);
    };
  }
  if (!Array.prototype.find) {
    Array.prototype.find = function (predicate, thisArg) {
      if (this == null) throw new TypeError('Array.prototype.find called on null or undefined');
      if (typeof predicate !== 'function') throw new TypeError('predicate must be a function');
      for (var i = 0; i < this.length; i++) {
        var value = this[i];
        if (predicate.call(thisArg, value, i, this)) return value;
      }
      return undefined;
    };
  }
  if (typeof window !== 'undefined' && typeof window.Map === 'undefined') {
    function SimpleMap() { this._ = Object.create(null); this.size = 0; }
    SimpleMap.prototype.get = function (k) { var sk = String(k); return Object.prototype.hasOwnProperty.call(this._, sk) ? this._[sk].v : undefined; };
    SimpleMap.prototype.set = function (k, v) { var sk = String(k); if (!Object.prototype.hasOwnProperty.call(this._, sk)) this.size++; this._[sk] = { k: k, v: v }; return this; };
    SimpleMap.prototype.delete = function (k) { var sk = String(k); if (Object.prototype.hasOwnProperty.call(this._, sk)) { delete this._[sk]; this.size--; return true; } return false; };
    SimpleMap.prototype.forEach = function (cb, thisArg) { var o = this._; for (var sk in o) { if (Object.prototype.hasOwnProperty.call(o, sk)) cb.call(thisArg, o[sk].v, o[sk].k, this); } };
    window.Map = SimpleMap;
  }
  var tg = (window.Telegram && window.Telegram.WebApp) ? window.Telegram.WebApp : null;

  function setThemeFromTelegram() {
    if (!tg) return;
    var themeParams = tg.themeParams || {};
    var root = document.documentElement;
    if (themeParams.bg_color) root.style.setProperty('--bg', themeParams.bg_color);
    if (themeParams.text_color) root.style.setProperty('--text', themeParams.text_color);
    if (themeParams.hint_color) root.style.setProperty('--muted', themeParams.hint_color);
    if (themeParams.button_color) root.style.setProperty('--primary', themeParams.button_color);
    if (themeParams.secondary_bg_color) root.style.setProperty('--card', themeParams.secondary_bg_color);
    if (themeParams.section_separator_color) root.style.setProperty('--border', themeParams.section_separator_color);
  }

  function formatPrice(value) {
    try { return value.toLocaleString('ru-RU') + ' ₽'; } catch (e) { return value + ' ₽'; }
  }

  function showNotification(title, message, callback) {
    // Создаем собственное модальное окно для совместимости
    var modal = document.createElement('div');
    modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:10000;';
    
    var modalContent = document.createElement('div');
    modalContent.style.cssText = 'background:var(--card,white);border-radius:12px;padding:20px;max-width:300px;margin:20px;box-shadow:0 4px 20px rgba(0,0,0,0.3);';
    
    var titleEl = document.createElement('h3');
    titleEl.textContent = title;
    titleEl.style.cssText = 'margin:0 0 10px 0;color:var(--text,black);font-size:18px;';
    
    var messageEl = document.createElement('p');
    messageEl.textContent = message;
    messageEl.style.cssText = 'margin:0 0 20px 0;color:var(--text,black);line-height:1.4;';
    
    var button = document.createElement('button');
    button.textContent = 'OK';
    button.style.cssText = 'background:var(--primary,#007bff);color:white;border:none;padding:10px 20px;border-radius:6px;cursor:pointer;width:100%;';
    button.addEventListener('click', function() {
      document.body.removeChild(modal);
      if (callback) callback();
    });
    
    modalContent.appendChild(titleEl);
    modalContent.appendChild(messageEl);
    modalContent.appendChild(button);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Закрытие по клику на фон
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        document.body.removeChild(modal);
        if (callback) callback();
      }
    });
  }

  var state = {
    cafe: {
      name: 'You Coffee (Nalchik)',
      hoursToday: 'Пн–Пт: 8:00–20:00 · Сб–Вс: 9:00–18:00',
      addresses: [
        { id: 'a1', label: 'г. Примерск, ул. Кофейная, 5', map: 'https://yandex.ru/maps/?text=Примерск%2C%20Кофейная%2C%205' },
        { id: 'a2', label: 'г. Примерск, пр-т Центральный, 10', map: 'https://yandex.ru/maps/?text=Примерск%2C%20Центральный%2C%2010' },
        { id: 'a3', label: 'г. Примерск, ул. Парковая, 3', map: 'https://yandex.ru/maps/?text=Примерск%2C%20Парковая%2C%203' }
      ],
      selectedAddressIndex: 0
    },
    menu: [],
    categories: [],
    cart: new Map(),
    activeCategory: null
  };

  function $(sel) { return document.querySelector(sel); }

  function getSelectedAddress() {
    var addresses = state.cafe.addresses || [];
    var idx = state.cafe.selectedAddressIndex || 0;
    if (idx < 0 || idx >= addresses.length) idx = 0;
    return addresses[idx] || null;
  }

  function renderCafeInfo() {
    var nameEl = $('#cafe-name');
    if (nameEl) nameEl.textContent = state.cafe.name;
    var hoursEl = $('#today-hours');
    if (hoursEl) hoursEl.textContent = state.cafe.hoursToday;
    renderAddresses();
  }

  function renderAddresses() {
    var listEl = document.getElementById('address-list');
    var selectedEl = document.getElementById('selected-address');
    var mapLink = document.getElementById('map-link');
    var toggleBtn = document.getElementById('toggle-addresses');
    if (!selectedEl || !listEl || !mapLink || !toggleBtn) return;

    var addresses = state.cafe.addresses && state.cafe.addresses.length ? state.cafe.addresses : [];
    if (!addresses.length) {
      addresses = [{ id: 'ax', label: 'Адрес не задан', map: '#' }];
      state.cafe.addresses = addresses;
      state.cafe.selectedAddressIndex = 0;
    }
    var idx = state.cafe.selectedAddressIndex || 0;
    if (idx < 0 || idx >= addresses.length) idx = 0;
    selectedEl.textContent = addresses[idx].label;
    mapLink.href = addresses[idx].map || '#';

    listEl.innerHTML = '';
    addresses.forEach(function (addr, i) {
      var li = document.createElement('li');
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'address__item';
      btn.textContent = addr.label;
      if (i === idx) btn.setAttribute('aria-current', 'true');
      btn.addEventListener('click', function () { selectAddress(i); });
      li.appendChild(btn);
      listEl.appendChild(li);
    });

    var expanded = !listEl.hidden;
    toggleBtn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    if (expanded) toggleBtn.classList.add('rotated'); else toggleBtn.classList.remove('rotated');
  }

  function toggleAddresses() {
    var listEl = document.getElementById('address-list');
    var toggleBtn = document.getElementById('toggle-addresses');
    if (!listEl || !toggleBtn) return;
    var willExpand = listEl.hidden;
    listEl.hidden = !listEl.hidden;
    toggleBtn.setAttribute('aria-expanded', willExpand ? 'true' : 'false');
    if (willExpand) toggleBtn.classList.add('rotated'); else toggleBtn.classList.remove('rotated');
  }

  function selectAddress(i) {
    state.cafe.selectedAddressIndex = i;
    var listEl = document.getElementById('address-list');
    var toggleBtn = document.getElementById('toggle-addresses');
    if (listEl) listEl.hidden = true;
    if (toggleBtn) { toggleBtn.setAttribute('aria-expanded', 'false'); toggleBtn.classList.remove('rotated'); }
    // Clear cart to avoid mixing items from different addresses
    state.cart = new Map();
    // Сбрасываем активную категорию при смене ресторана
    state.activeCategory = null;
    renderAddresses();
    renderCategories(); // Обновляем категории для нового ресторана
    renderMenu();
    updateOrderPanel();
    updateCartSummary();
  }

  function renderCategories() {
    var categoryList = document.getElementById('category-list');
    if (!categoryList) return;
    
    // Очищаем список, оставляя только кнопку "Все"
    var allButton = categoryList.querySelector('[data-category="all"]');
    categoryList.innerHTML = '';
    if (allButton) {
      var allItem = document.createElement('li');
      allItem.className = 'brand-menu__item';
      allItem.appendChild(allButton);
      categoryList.appendChild(allItem);
    }
    
    // Получаем ID выбранного ресторана
    var selectedAddress = getSelectedAddress();
    var selectedRestaurantId = null;
    
    if (selectedAddress && selectedAddress.id) {
      // Извлекаем ID ресторана из addressId (формат: restaurant_ID)
      var match = selectedAddress.id.match(/restaurant_(\d+)/);
      if (match) {
        selectedRestaurantId = parseInt(match[1]);
      }
    }
    
    // Фильтруем категории по выбранному ресторану
    var filteredCategories = state.categories.filter(function (category) {
      // Если ресторан не выбран или у категории нет restaurant_id, показываем все
      if (!selectedRestaurantId || !category.restaurant_id) {
        return true;
      }
      return category.restaurant_id === selectedRestaurantId;
    });
    
    // Добавляем отфильтрованные категории
    filteredCategories.forEach(function (category) {
      var li = document.createElement('li');
      li.className = 'brand-menu__item';
      
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'chip';
      button.setAttribute('data-category', category.slug);
      button.textContent = category.name;
      
      li.appendChild(button);
      categoryList.appendChild(li);
    });
    
    // Обновляем обработчики событий
    setupCategoryHandlers();
  }

  function renderMenu() {
    var grid = $('#menu-grid');
    if (!grid) return;
    grid.innerHTML = '';
    var selAddr = getSelectedAddress();
    var selId = selAddr ? selAddr.id : null;
    
    // Получаем ID выбранного ресторана
    var selectedRestaurantId = null;
    if (selAddr && selAddr.id) {
      var match = selAddr.id.match(/restaurant_(\d+)/);
      if (match) {
        selectedRestaurantId = parseInt(match[1]);
      }
    }
    
    var items = state.menu.filter(function (i) {
      // Фильтрация по категории
      var okCat = !state.activeCategory || i.category === state.activeCategory;
      
      // Фильтрация по ресторану
      var okRestaurant = true;
      if (selectedRestaurantId && i.restaurant_id) {
        okRestaurant = i.restaurant_id === selectedRestaurantId;
      } else if (selectedRestaurantId && !i.restaurant_id) {
        // Если у товара нет restaurant_id, но ресторан выбран, используем старую логику addressId
        okRestaurant = !i.addressId || i.addressId === selId;
      } else if (!selectedRestaurantId) {
        // Если ресторан не выбран, показываем все товары
        okRestaurant = true;
      }
      
      return okCat && okRestaurant;
    });
    
    if (!items || !items.length) {
      var empty = document.createElement('div');
      empty.className = 'menu-empty';
      empty.textContent = 'Нет позиций в этой категории';
      grid.appendChild(empty);
      return;
    }
    items.forEach(function (item) {
      var card = document.createElement('div');
      card.className = 'card';
      
      // Добавляем изображение товара если есть
      if (item.photo) {
        var img = document.createElement('img');
        img.className = 'card__image';
        img.src = item.photo;
        img.alt = item.name;
        img.style.cssText = 'width: 100%; height: 150px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;';
        card.appendChild(img);
      }
      
      var title = document.createElement('h3');
      title.className = 'card__title';
      title.textContent = item.name;
      var desc = document.createElement('p');
      desc.className = 'card__desc';
      desc.textContent = item.description || '';
      
      // Добавляем размер если есть
      if (item.size) {
        var size = document.createElement('span');
        size.className = 'card__size';
        size.textContent = item.size;
        size.style.cssText = 'font-size: 12px; color: var(--muted); background: var(--card); padding: 2px 6px; border-radius: 4px; margin-left: 8px;';
        title.appendChild(size);
      }
      
      var meta = document.createElement('div');
      meta.className = 'card__meta';
      var price = document.createElement('span');
      price.className = 'price';
      price.textContent = formatPrice(item.price);
      var btn = document.createElement('button');
      btn.className = 'btn btn-primary';
      btn.textContent = 'Добавить';
      btn.addEventListener('click', function () { addToCart(item.id); });
      
      // Отключаем кнопку если товар недоступен
      if (!item.is_available || (item.stock !== null && item.stock <= 0)) {
        btn.disabled = true;
        btn.textContent = 'Недоступен';
        btn.style.opacity = '0.5';
      }
      
      meta.appendChild(price);
      meta.appendChild(btn);
      card.appendChild(title);
      card.appendChild(desc);
      card.appendChild(meta);
      grid.appendChild(card);
    });
  }

  function updateCartSummary() {
    var summary = $('#cart-summary');
    if (!summary) return;
    var totalQty = 0;
    var totalSum = 0;
    state.cart.forEach(function (entry) { totalQty += entry.qty; totalSum += entry.qty * entry.item.price; });
    if (totalQty === 0) {
      summary.textContent = 'Корзина пуста';
      if (tg && tg.MainButton) tg.MainButton.hide();
      var panel = document.getElementById('order-panel');
      if (panel) panel.hidden = true;
      return;
    }
    summary.textContent = 'В корзине: ' + totalQty + ' · ' + formatPrice(totalSum);
    if (tg && tg.MainButton) {
      tg.MainButton.setParams({ text: 'Оформить (' + totalQty + ') — ' + totalSum + '₽' });
      tg.MainButton.show();
    }
  }

  function addToCart(id) {
    var item = state.menu.find(function (m) { return m.id === id; });
    if (!item) return;
    var current = state.cart.get(id) || { item: item, qty: 0 };
    current.qty += 1;
    state.cart.set(id, current);
    if (tg && tg.HapticFeedback && tg.HapticFeedback.impactOccurred) tg.HapticFeedback.impactOccurred('light');
    updateOrderPanel();
    updateCartSummary();
  }

  function changeQty(id, delta) {
    var current = state.cart.get(id);
    if (!current) return;
    current.qty += delta;
    if (current.qty <= 0) state.cart.delete(id);
    updateOrderPanel();
    updateCartSummary();
  }

  function updateOrderPanel() {
    var list = $('#order-list');
    var totalEl = $('#order-total');
    var panel = document.getElementById('order-panel');
    var addrEl = document.getElementById('order-address');
    if (!list || !totalEl || !panel) return;
    list.innerHTML = '';
    var selAddr = getSelectedAddress();
    if (addrEl && selAddr) addrEl.textContent = selAddr.label;
    var total = 0;
    state.cart.forEach(function (entry) {
      var item = entry.item; var qty = entry.qty;
      var row = document.createElement('div');
      row.className = 'order-item';
      var left = document.createElement('div');
      left.textContent = item.name + ' · ' + formatPrice(item.price);
      var right = document.createElement('div');
      right.className = 'qty';
      var minus = document.createElement('button'); minus.className = 'btn'; minus.textContent = '−';
      var count = document.createElement('span'); count.textContent = String(qty);
      var plus = document.createElement('button'); plus.className = 'btn'; plus.textContent = '+';
      minus.addEventListener('click', function () { changeQty(item.id, -1); });
      plus.addEventListener('click', function () { changeQty(item.id, +1); });
      right.appendChild(minus);
      right.appendChild(count);
      right.appendChild(plus);
      row.appendChild(left);
      row.appendChild(right);
      list.appendChild(row);
      total += item.price * qty;
    });
    totalEl.textContent = formatPrice(total);
    panel.hidden = state.cart.size === 0;
  }

  function sendOrder() {
    var order = [];
    var totalSum = 0;
    state.cart.forEach(function (entry) {
      order.push({ id: entry.item.id, name: entry.item.name, qty: entry.qty, price: entry.item.price });
      totalSum += entry.qty * entry.item.price;
    });
    var selAddr = getSelectedAddress();
    
    // Извлекаем ID ресторана из выбранного адреса
    var restaurantId = null;
    if (selAddr && selAddr.id) {
      var match = selAddr.id.match(/restaurant_(\d+)/);
      if (match) {
        restaurantId = parseInt(match[1]);
      }
    }
    
    // Формируем данные заказа для отправки на сервер
    var orderData = {
      order: order,
      totalSum: totalSum,
      address: selAddr ? selAddr.label : 'Не указан',
      restaurant_id: restaurantId, // Добавляем ID ресторана
      timestamp: new Date().toISOString(),
      user: null
    };
    
    // Добавляем информацию о пользователе, если доступна
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {
      var user = tg.initDataUnsafe.user;
      orderData.user = {
        id: user.id,
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        username: user.username || ''
      };
    }
    
    console.log('Отправляем заказ:', orderData);
    
    // Отправляем POST-запрос на API админ-панели
    var apiUrl = 'http://localhost:8000/api/orders';
    
    requestCompat(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(orderData)
    }).then(function (response) {
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
      
      return response.json().then(function(data) {
        console.log('Response data:', data);
        
        if (response.ok && data.status === 'success') {
          if (tg) {
            showNotification('Успех', 'Заказ успешно отправлен!', function() {
              if (tg.close) tg.close();
            });
          } else {
            alert('Заказ успешно отправлен! (демо режим)');
          }
        } else {
          var errorMsg = data.message || 'Неизвестная ошибка';
          console.error('API error:', errorMsg);
          throw new Error('Ошибка API: ' + errorMsg);
        }
      });
    }).catch(function (error) {
      console.error('Ошибка отправки заказа:', error);
      
      var errorMessage = 'Ошибка отправки заказа';
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorMessage = 'Ошибка сети. Проверьте подключение к интернету.';
      } else if (error.message.includes('CORS')) {
        errorMessage = 'Ошибка CORS. Проверьте настройки сервера.';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      if (tg) {
        showNotification('Ошибка', errorMessage);
      } else {
        alert(errorMessage + ' (демо режим)');
      }
    });
  }

  function requestCompat(path, opts) {
    return new Promise(function (resolve, reject) {
      if (typeof fetch === 'function') {
        fetch(path, opts).then(resolve).catch(reject);
        return;
      }
      // XHR fallback for older WKWebView
      try {
        var xhr = new XMLHttpRequest();
        xhr.open((opts && opts.method) || 'GET', path, true);
        var headers = (opts && opts.headers) || {};
        for (var h in headers) if (Object.prototype.hasOwnProperty.call(headers, h)) xhr.setRequestHeader(h, headers[h]);
        xhr.onreadystatechange = function () {
          if (xhr.readyState === 4) {
            var res = {
              ok: xhr.status >= 200 && xhr.status < 300,
              status: xhr.status,
              json: function () { try { return Promise.resolve(JSON.parse(xhr.responseText)); } catch (e) { return Promise.reject(e); } }
            };
            resolve(res);
          }
        };
        xhr.onerror = reject;
        xhr.send((opts && opts.body) || null);
      } catch (e) { reject(e); }
    });
  }

  function firstSuccessfulFetch(paths, opts) {
    return new Promise(function (resolve, reject) {
      var i = 0;
      function tryNext() {
        if (i >= paths.length) { reject(new Error('No path succeeded')); return; }
        requestCompat(paths[i], opts).then(function (res) {
          if (!res.ok) { i++; tryNext(); return; }
          resolve(res);
        }).catch(function () { i++; tryNext(); });
      }
      tryNext();
    });
  }

  function loadRestaurants() {
    var apiUrl = 'http://localhost:8000/api/restaurants';
    
    return requestCompat(apiUrl, { cache: 'no-store' })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.restaurants && Array.isArray(data.restaurants)) {
          // Преобразуем данные ресторанов в формат адресов
          state.cafe.addresses = data.restaurants.map(function(restaurant, index) {
            return {
              id: 'restaurant_' + restaurant.id,
              label: restaurant.name + ' - ' + restaurant.address,
              map: 'https://yandex.ru/maps/?text=' + encodeURIComponent(restaurant.address)
            };
          });
          
          // Обновляем название кафе
          if (data.restaurants.length > 0) {
            state.cafe.name = data.restaurants[0].name;
          }
        }
      })
      .catch(function (error) {
        console.warn('Ошибка загрузки ресторанов:', error);
        // Используем fallback данные
      });
  }

  function loadCategories() {
    var apiUrl = 'http://localhost:8000/api/categories';
    
    return requestCompat(apiUrl, { cache: 'no-store' })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.categories && Array.isArray(data.categories)) {
          return data.categories.map(function(category) {
            return {
              id: category.id,
              name: category.name,
              slug: category.name.toLowerCase().replace(/\s+/g, '_'),
              restaurant_id: category.restaurant_id
            };
          });
        }
        return [];
      })
      .catch(function (error) {
        console.warn('Ошибка загрузки категорий:', error);
        // Fallback категории
        return [
          { id: 1, name: 'Напитки', slug: 'drinks', restaurant_id: 1 },
          { id: 2, name: 'Выпечка', slug: 'desserts', restaurant_id: 1 },
          { id: 3, name: 'Десерты', slug: 'desserts', restaurant_id: 1 }
        ];
      });
  }

  function loadMenu() {
    // Сначала пробуем загрузить из API админ-панели
    var apiUrl = 'http://localhost:8000/api/products'; // URL админ-панели
    
    return firstSuccessfulFetch([apiUrl, './menu.json', '/menu.json'], { cache: 'no-store' })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        var items;
        
        // Проверяем формат ответа API
        if (data.products && Array.isArray(data.products)) {
          // Данные из API админ-панели
          items = data.products.map(function(item) {
            return {
              id: item.id,
              name: item.name,
              price: item.discount_price || item.price,
              description: item.description,
              category: item.category ? item.category.name.toLowerCase().replace(/\s+/g, '_') : 'other',
              size: item.size,
              photo: item.photo,
              is_available: item.is_available,
              stock: item.stock,
              restaurant_id: item.restaurant_id
            };
          });
        } else if (Array.isArray(data)) {
          // Старый формат JSON
          items = data;
        } else {
          throw new Error('Invalid data format');
        }
        
        state.menu = items;
        return items;
      })
      .catch(function (error) {
        console.warn('Ошибка загрузки меню:', error);
        // Fallback данные
        state.menu = [
          { id: 1, name: 'Американо', price: 150, description: 'Кофе 250 мл', category: 'drinks', addressId: 'a1' },
          { id: 2, name: 'Капучино', price: 210, description: 'Кофе с молоком 300 мл', category: 'drinks', addressId: 'a1' },
          { id: 3, name: 'Латте', price: 230, description: 'Нежный латте 300 мл', category: 'drinks', addressId: 'a1' },
          { id: 4, name: 'Круассан', price: 180, description: 'Сливочный, свежая выпечка', category: 'desserts', addressId: 'a2' },
          { id: 5, name: 'Чизкейк', price: 260, description: 'Классический Нью-Йорк', category: 'desserts', addressId: 'a2' }
        ];
      });
  }

  function setActiveCategory(slug) {
    state.activeCategory = slug;
    var chips = document.querySelectorAll('.brand-menu .chip');
    if (chips && chips.forEach) {
      chips.forEach(function (btn) {
        var btnCat = btn.dataset.category;
        var isActive = (slug == null && btnCat === 'all') || (slug != null && btnCat === slug);
        if (isActive) btn.classList.add('chip--active'); else btn.classList.remove('chip--active');
      });
    }
    renderMenu();
    var menuSection = document.querySelector('.menu');
    if (menuSection && menuSection.scrollIntoView) menuSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function setupCategoryHandlers() {
    var chips = document.querySelectorAll('.brand-menu .chip');
    if (chips && chips.forEach) {
      chips.forEach(function (btn) {
        btn.addEventListener('click', function () {
          var slug = btn.dataset.category;
          if (slug === 'all') { setActiveCategory(null); return; }
          if (state.activeCategory === slug) setActiveCategory(null); else setActiveCategory(slug);
        });
      });
    }
  }

  function setupUI() {
    var confirmBtn = document.getElementById('confirm-order');
    if (confirmBtn) confirmBtn.addEventListener('click', sendOrder);
    var contBtn = document.getElementById('continue');
    if (contBtn) contBtn.addEventListener('click', function () {
      var menuSection = document.querySelector('.menu');
      if (menuSection && menuSection.scrollIntoView) menuSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    
    // Настраиваем обработчики категорий
    setupCategoryHandlers();
    
    if (tg && tg.MainButton && tg.MainButton.onClick) tg.MainButton.onClick(sendOrder);
    var toggleBtn = document.getElementById('toggle-addresses');
    if (toggleBtn) toggleBtn.addEventListener('click', toggleAddresses);
  }

  function updateThemeIndicator() {
    var el = document.getElementById('theme-indicator');
    if (!tg || !el) return;
    var scheme = tg.colorScheme || 'light';
    el.style.opacity = 1;
    el.style.background = scheme === 'dark' ? '#6ea8fe' : '#2b7cff';
  }

  function init() {
    if (!tg) {
      var notice = document.getElementById('tg-notice');
      if (notice) notice.hidden = false;
      console.log('Telegram WebApp не доступен - работаем в демо-режиме');
    } else {
      console.log('Telegram WebApp инициализирован');
      console.log('initDataUnsafe:', tg.initDataUnsafe);
      console.log('initData:', tg.initData);
      
      // Дополнительная диагностика
      if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
        console.log('User data:', tg.initDataUnsafe.user);
        console.log('User ID:', tg.initDataUnsafe.user.id);
      }
      
      setThemeFromTelegram();
      if (tg.ready) tg.ready();
      if (tg.expand) tg.expand();
    }
    renderCafeInfo();
    
    // Загружаем данные о ресторанах, категориях и меню параллельно
    Promise.all([
      loadRestaurants(),
      loadCategories(),
      loadMenu()
    ]).then(function (results) {
      // results[0] - restaurants, results[1] - categories, results[2] - menu
      state.categories = results[1] || [];
      
      renderCafeInfo(); // Обновляем информацию о кафе после загрузки ресторанов
      renderCategories(); // Отображаем категории
      renderMenu();
      setupUI();
      setActiveCategory(null);
      updateOrderPanel();
      updateCartSummary();
      updateThemeIndicator();
      if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.ready) {
        window.Telegram.WebApp.ready();
      }
    });
  }

  if (tg && tg.onEvent) tg.onEvent('themeChanged', function () { setThemeFromTelegram(); updateThemeIndicator(); });

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
