import Component from "./component.js";

export default class Question extends Component{
    setup() {
        fetch('http://127.0.0.1:8081/api/question')
            .then(res => {
                res.json().then( res => this.setState(res));
            }).catch(err => {
                console.error(err);
        })
    }

    template() {
        return `
            <h1>Practice Computer Science interview questions!</h1>
            <h2>${this.$state && this.$state.question}<h2/>
        `
    }

    setState(newState) {
        this.$state = { ...this.$state, question: newState.question, id: newState.id};
        this.render();
    }
}