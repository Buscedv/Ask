<template>
    <nav>
        <div class="row">
            <div class="col-md-3 col-xs-12 r-separator">
                <div class="row navbar-row">
                    <div class="col-md-6 col-xs-1" id="menu-btn-holder">
                        <button @click="$emit('toggle-sidebar')"><font-awesome-icon icon="bars"/></button>
                    </div>
                    <div class="col-md-6 col-xs-11" id="logo-holder">
                        <img src="../assets/img/banner.png" alt="Docual" @click="goHome()">
                    </div>
                </div>
            </div>
            <div class="col-md-7" id="links">
                <div class="row navbar-row">
                    <a v-for="(link, index) in navbarLinks" :key="index" class="nav-item" :href="link.link" v-text="link.title"></a>
                </div>
            </div>
            <div class="col-md-2" id="icons">
                <div class="row navbar-row">
                    <a v-for="(icon, index) in navbarIcons" :key="index" class="nav-item navbar-icon" :href="icon.link"><font-awesome-icon :icon="icon.icon"/></a>
                </div>
            </div>
        </div>
    </nav>
</template>

<script>
    import config from '../../public/config.json';

    export default {
        name: 'Navbar',
        data() {
            return {
                navbarLinks: [],
                navbarIcons: [],
            }
        },
        methods: {
            goHome() {
                window.location.href = '/';
            },
        },
        mounted() {
            this.navbarLinks = config.navLinks;
            this.navbarIcons = config.navIcons;

        },
    }
</script>

<style scoped>
    nav {
        height: 70px;
        background-color: #fff;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        display: flex;
        align-items: center;
        border-bottom: 2px solid var(--light);
        z-index: 99;
    }

    .row {
        width: 100%;
    }

    #menu-btn-holder, #logo-holder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
    }

    #logo-holder img {
        max-height: 22px;
        margin-left: auto;
    }

    #logo-holder img:hover {
        cursor: pointer;
    }

    #menu-btn-holder button {
        border: none;
        font-size: 1.2em;
        padding: 10px;
        color: var(--light-dark);
        background: none;
    }

    #menu-btn-holder:hover button {
        cursor: pointer;
        color: var(--dark);
    }

    .r-separator {
        border-right: 2px solid var(--light);
    }

    .navbar-row {
        display: flex;
        align-items: center;
        height: 100%;
        padding-left: 10px;
        padding-right: 10px;
    }

    .nav-item {
        margin-left: 10px;
        margin-right: 10px;
        padding: 5px;
        font-size: 1.2rem;
        text-decoration: none;
        color: var(--dark);
    }

    .navbar-icon {
        margin-left: auto;
        color: var(--almost-dark);
    }

    @media screen and (max-width: 1025px){
        #links, #icons {
            display: none;
        }

        .r-separator {
            border: none;
            padding-right: 1px;
        }

        #logo-holder img {
            margin-right: auto;
        }
    }

</style>
