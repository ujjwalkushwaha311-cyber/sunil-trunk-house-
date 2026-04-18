<header>
    <nav class="navbar">
        <div class="logo">
            <img src="{% static 'logo/sth_logo.webp' %}" alt="Logo">
        </div>

        <ul class="nav-links">
            <li>
                <a href="{% url 'home' %}" class="{% if request.resolver_match.url_name == 'home' %}active-link{% endif %}">Home</a>
            </li>

            <li class="dropdown">
                <a href="#" class="{% if request.resolver_match.url_name in 'almirah trunk coller stand' %}active-link{% endif %}">Products</a>
                <ul class="dropdown-menu">
                    <li><a href="{% url 'almirah' %}">Almirah</a></li>
                    <li><a href="{% url 'trunk' %}">Trunk Box</a></li>
                    <li><a href="{% url 'coller' %}">Coller</a></li>
                    <li><a href="{% url 'stand' %}">Steel Stand</a></li>
                </ul>
            </li>

            <li>
                <a href="{% url 'authenticity' %}" class="{% if request.resolver_match.url_name == 'authenticity' %}active-link{% endif %}">Check Authenticity</a>
            </li>
            <li>
                <a href="{% url 'about' %}" class="{% if request.resolver_match.url_name == 'about' %}active-link{% endif %}">About Us</a>
            </li>
            <li>
                <a href="{% url 'complain' %}" class="{% if request.resolver_match.url_name == 'complain' %}active-link{% endif %}">Complain</a>
            </li>
            <li>
                <a href="{% url 'contact' %}" class="{% if request.resolver_match.url_name == 'contact' %}active-link{% endif %}">Contact</a>
            </li>

            <li class="dropdown">
                <a href="#" class="{% if request.resolver_match.url_name in 'track_order track_complain' %}active-link{% endif %}">Track</a>
                <ul class="dropdown-menu">
                    <li><a href="{% url 'track_order' %}">Track Your Order</a></li>
                    <li><a href="{% url 'track_complain' %}">Track Your Complain</a></li>
                </ul>
            </li>
        </ul>
    </nav>
</header>