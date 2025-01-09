class Stack {
  top: any;
  items: any[];

  constructor() {
    this.top = -1;
    this.items = [];
  }

  get peek(): any {
    return this.items[this.top];
  }

  push(value: any) {
    this.top += 1;
    this.items[this.top] = value;
  }

  get pop(): any {
    this.top -= 1;
    return this.items[this.top + 1];
  }
}

export {Stack};
