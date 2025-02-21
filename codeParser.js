class CodeParser {
    static parse(code) {
        const [base, lesson] = code.split('-');
        return {
            section: parseInt(base.slice(0, 2)),
            circle: parseInt(base.slice(2)),
            lesson: lesson ? parseInt(lesson) : 0
        };
    }

    static compare(code, condition) {
        const target = this.parse(code);
        return condition.split(',').every(cond => {
            const [operator, value] = cond.split(/(>=|<=|=|>|<)/).filter(Boolean);
            const parsedValue = this.parse(value);
            
            return this.applyOperator(target, operator, parsedValue);
        });
    }

    static applyOperator(target, operator, condition) {
        const targetNum = target.section * 1000000 + target.circle * 1000 + target.lesson;
        const conditionNum = condition.section * 1000000 + condition.circle * 1000 + condition.lesson;
        
        switch(operator) {
            case '>=': return targetNum >= conditionNum;
            case '<=': return targetNum <= conditionNum;
            case '>': return targetNum > conditionNum;
            case '<': return targetNum < conditionNum;
            default: return targetNum === conditionNum;
        }
    }
}