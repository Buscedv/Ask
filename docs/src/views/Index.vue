<template>
    <main class="container-fluid">
        <Navbar @toggle-sidebar="sidebarStatus = !sidebarStatus"></Navbar>
        <ContentRoot :sidebarStatus="sidebarStatus" @changeSidebarStatus="changeSidebarStatus"></ContentRoot>
    </main>
</template>

<script>
    import Navbar from "../components/Navbar";
    import ContentRoot from "../components/ContentRoot";
    export default {
        name: 'Index',
        components: {ContentRoot, Navbar},
        data() {
            return {
                sidebarStatus: true,
            }
        },
        mounted() {
            window.addEventListener("resize", this.resizeChecker);
            this.resizeChecker();
        },
        destroyed() {
            window.removeEventListener("resize", this.resizeChecker);
        },
        methods: {
            resizeChecker() {
                if (window.innerWidth <= 1025) {
                    this.sidebarStatus = false;
                } else {
                    this.sidebarStatus = true;
                }
            },
            changeSidebarStatus(status) {
                this.sidebarStatus = status;
            },
        },
    }
</script>

<style scoped>
    main {
        height: 100vh;
        padding: 0;
        width: 100%;
    }
</style>