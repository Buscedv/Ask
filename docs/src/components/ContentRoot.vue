<template>
    <main>
        <div class="row">
            <div class="col-md-3 col-xs-7" v-if="sidebarStatus" id="sidebar">
                <Sidebar :links="links" :isMobile="isMobile"></Sidebar>
            </div>
            <div class="col-md-9 col-xs-12" :class="(isMobile && sidebarStatus) ? 'fade' : ''" id="doc-area" @click="docClicked()">
                <Doc @sidebarLinks="sidebarLinks"></Doc>
            </div>
        </div>
    </main>
</template>

<script>
    import Sidebar from "./Sidebar";
    import Doc from "./Doc";
    export default {
        name: 'ContentRoot',
        components: {Doc, Sidebar},
        props: ['sidebarStatus'],
        methods: {
            sidebarLinks(links) {
                this.links = links;
            },
            docClicked() {
                if (this.sidebarStatus && this.isMobile) {
                    this.$emit('changeSidebarStatus', false)
                }
            },
            checkWindowSize() {
                if (window.innerWidth <= 1025) {
                    this.isMobile = true;
                } else {
                    this.isMobile = false;
                }
            },
        },
        data() {
            return {
                isMobile: false,
                links: [],
            }
        },
        mounted() {
            window.addEventListener("resize", this.checkWindowSize);
            this.checkWindowSize();
        },
        destroyed() {
            window.removeEventListener("resize", this.checkWindowSize);
        },
    }
</script>

<style scoped>
    main {
        height: 100vh;
        width: 100%;
    }

    #doc-area {
        overflow-x: hidden;
        max-width: available;
        height: 100%;
        padding-right: 80px;
    }

    #sidebar {
        overflow-x: hidden;
        max-width: available;
        height: 100%;
        padding: 0;
        width: 100%;
    }

    #sidebar * {
        width: inherit;
        height: 100%;
    }

    .fade {
        opacity: 50%;
    }

</style>
