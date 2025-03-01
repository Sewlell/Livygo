class CodeParser {
    static parse(code) {
        try {
            const [base, lesson] = code.split('-');
            return {
                section: parseInt(base?.slice(0, 2)) || 0,
                circle: parseInt(base?.slice(2)) || 0,
                lesson: lesson ? parseInt(lesson) : 0,
                numeric: parseInt(`${base?.padEnd(4, '0')}${lesson?.padStart(3, '0') || '000'}`)
            };
        } catch (e) {
            console.error('Parse error:', e);
            return { section: 0, circle: 0, lesson: 0, numeric: 0 };
        }
    }

    static compare(code, condition) {
        if (!condition?.trim()) return true;
        try {
            const target = this.parse(code);
            return condition.split(',').every(cond => {
                const match = cond.match(/(>=|<=|>|<|=)?([\d-]+)/);
                if (!match) return false;
                const operator = match[1] || '=';
                const parsedValue = this.parse(match[2]);
                return this.applyOperator(target, operator, parsedValue);
            });
        } catch (e) {
            console.error('Compare error:', e);
            return true;
        }
    }

    static applyOperator(target, operator, condition) {
        const targetNum = target.numeric;
        const conditionNum = condition.numeric;
        switch(operator) {
            case '>=': return targetNum >= conditionNum;
            case '<=': return targetNum <= conditionNum;
            case '>': return targetNum > conditionNum;
            case '<': return targetNum < conditionNum;
            default: return targetNum === conditionNum;
        }
    }
}