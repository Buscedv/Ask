<template>
    <aside>
        <div class="sidebar">
            <div class="header">
                <a class="sidebar-btn-c" @click="toggleSearch" v-if="!isSearch" v-show="!isMobile"><font-awesome-icon icon="search"/></a>
                <a class="sidebar-btn-c" @click="toggleSearch" v-if="isSearch"><font-awesome-icon icon="arrow-left"/></a>
                <a class="sidebar-btn" @click="smoothScroll(filteredLinks[0].link)" v-text="homeBtnText"></a>
            </div>
            <div class="sidebar-search" v-if="isSearch">
                <input type="search" :placeholder="searchHint" v-model="search" ref="searchBox">
            </div>
            <div id="no-results" v-if="noResults">
                    <img src="../assets/img/no_results.png" alt="no results">
            </div>
            <div class="sidebar-items" v-if="shouldShowItems">
                <span v-for="(link, index) in filteredLinks" :key="index" class="sidebar-item">
                    <a class="sidebar-link" @click="smoothScroll(link.link)" v-text="link.title" v-if="link.type === 'H1'"></a>
                    <div class="sidebar-link sidebar-sub-items" v-else>
                        <a class="sidebar-link sidebar-link-sub" @click="smoothScroll(link.link)" v-text="link.title"></a>
                    </div>
                </span>
            </div>
        </div>
    </aside>
</template>

<script>
    import config from '../../public/config.json';

    export default {
        name: 'Sidebar',
        props: ['links', 'isMobile'],
        data() {
            return {
                isSearch: false,
                search: '',
                homeBtnText: '',
                searchHint: '',
            }
        },
        methods: {
            toggleSearch() {
                this.isSearch = !this.isSearch;
                this.search = '';
                this.$nextTick(() => {
                    this.$refs.searchBox.focus()
                })
            },
            smoothScroll(id) {
                document.querySelector(id).scrollIntoView({block: 'center'});

                const actives = document.querySelectorAll('.activeScrollTo')
                for (let i = 0; i < actives.length; i++) {
                    actives[i].classList.remove('activeScrollTo')
                }
                document.querySelector(id).classList.add('activeScrollTo')
            },
        },
        computed: {
            filteredLinks() {
                return this.links.filter(link => {
                    return link.text.toLowerCase().includes(this.search.toLowerCase())
                })
            },
            noResults() {
                if (!this.isSearch) {
                    return false;
                }

                if (this.filteredLinks.length === 0 || this.filteredLinks.length === this.links.length) {
                    return true;
                }

                return false;
            },
            shouldShowItems() {
                if (this.isSearch && this.noResults) {
                    return false;
                }

                return true;
            },
        },
        mounted() {
            this.searchHint = config.searchHint;
            this.homeBtnText = config.homeBtnText;
        }
    }
</script>

<style scoped>
    aside {
        height: 100%;
        background-color: var(--light);
        position: fixed;
        max-width: inherit;
        z-index: 98;
    }

    .sidebar {
        max-width: 100%;
        border-right: 2px solid var(--light-hover);
        padding: 25px;
        overflow-y: auto;
        height: inherit;
    }

    .sidebar-items, .sidebar-sub-items {
        height: fit-content;
        margin-top: 0;
        margin-bottom: 20px !important;
    }

    .header {
        margin-top: 60px;
        padding-top: 10px;
        width: 100%;
        margin-bottom: 20px;
        padding-bottom: 20px;
    }

    .header h1 {
        font-size: 2em;
        color: var(--light-dark);

    }

    .header .row {
        display: flex;
        align-items: center;
    }

    .header .row * {
        padding: 2px;
    }

    .sidebar-link {
        font-size: 1.1em;
        color: var(--dark);
        width: 100%;
        float: left;
        border-left: 2px solid var(--accent);
        padding-left: 8px;
        padding-top: 6px;
        padding-bottom: 6px;
        text-decoration: none;
    }

    .sidebar-link:hover:not(.sidebar-sub-items) {
        color: var(--accent);
        cursor: pointer;
        background-color: var(--light-hover);
        border-left: 2px solid var(--accent);
    }

    .sidebar-sub-items {
        margin-left: 8px;
        border-color: var(--light-hover);
    }

    .sidebar-link-sub {
        border-color: var(--light);
        font-size: 1em;
        font-family: 'Roboto Light', sans-serif;
        color: var(--almost-dark);
    }

    .sidebar-btn, .sidebar-btn-c {
        background-color: var(--accent);
        color: var(--white);
        text-align: center;
        font-size: 1em;
        margin-bottom: 25px;
    }

    .sidebar-btn {
        padding: 10px;
        padding-left: 25px;
        padding-right: 25px;
        border-radius: 10px;
        width: auto;
    }

    .sidebar-btn:hover, .sidebar-btn-c:hover {
        background-color: var(--accent-hover);
        cursor: pointer;
    }

    .sidebar-btn-c {
        padding: 5px;
        border-radius: 50%;
        height: 35px;
        width: 35px;
        display: flex;
        align-items: center;
    }

    .sidebar-btn-c * {
        margin-left: auto;
        margin-right: auto;
    }

    .sidebar-search {
        width: 100%;
        text-align: center;
    }

    .sidebar-search input {
        width: 100%;
        padding: 10px;
        background-color: var(--white);
        color: var(--dark);
        border: 1px solid var(--light-hover);
        border-radius: 10px;
        font-size: 1.1em;
        margin-bottom: 20px;
    }

    #no-results {
        width: 100%;
        display: flex;
        align-items: center;
        height: 50%;
    }

    #no-results img {
        height: 100px;
        margin-left: auto;
        margin-right: auto;
    }
</style>
