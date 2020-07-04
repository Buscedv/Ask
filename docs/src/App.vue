<template>
    <div id="app">
        <Index></Index>
    </div>
</template>

<script>
    import '../public/colors.css'
    import './assets/css/flexboxgrid.min.css'
    import Index from "./views/Index";

    import config from '../public/config.json';

    export default {
        name: 'App',
        components: {Index},
        mounted() {
            document.title = config.title;
        }
    }
</script>

<style>
    @import url('https://fonts.googleapis.com/css?family=Roboto|Open+Sans|Roboto+Mono&display=swap');

    body {
        font-family: 'Roboto', sans-serif;
        padding: 0;
        margin: 0;
        height: 100vh;
        width: 100%;
        background: var(--white);
    }

    #app {
        height: 100%;
        width: 100%;
        overflow: hidden;
    }

    * {
        box-shadow: none !important;
        outline: none !important;
        scroll-behavior: smooth;
    }

    ::-webkit-scrollbar {
        width: 0;
    }

    code, pre {
        font-family: 'Roboto Mono', monospace;
    }

    /** {*/
    /*    outline: 1px solid red !important;*/
    /*}*/
</style>
