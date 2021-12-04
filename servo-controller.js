const PiServo = require('pi-servo');
const JSONdb = require('simple-json-db');
const db = new JSONdb('./database.json');

const sv1 = new PiServo(4);
const eachAngle = 60;

function initDB() {
    if (!db.has('currentDegree') && !db.has('currentDirection')) {
        db.set('currentDegree', 0)
        db.set('currentDirection', 1);
    }
}

class ServoController {
    constructor() {
        initDB();
    }

    feedOnce(runWiggler = false) {
        const parent = this;
        sv1.open().then(function () {

            const result = parent.mathAngle(db.get('currentDegree'), db.get('currentDirection'));

            sv1.setDegree(result.currentAngle); // 0 - 180
            db.set('currentDegree', result.currentAngle)
            db.set('currentDirection', result.direction);

            if (runWiggler) {
                parent.wiggler();
            }

        });
    }

    wiggler() {
        sv1.open().then(async function () {

            await new Promise(resolve => setTimeout(resolve, 500));
            sv1.setDegree(db.get('currentDegree') + 10); // 0 - 180
            await new Promise(resolve => setTimeout(resolve, 100));
            sv1.setDegree(db.get('currentDegree') - 10); // 0 - 180
            await new Promise(resolve => setTimeout(resolve, 100));
            sv1.setDegree(db.get('currentDegree') + 10); // 0 - 180
            await new Promise(resolve => setTimeout(resolve, 100));
            sv1.setDegree(db.get('currentDegree') - 10); // 0 - 180
            await new Promise(resolve => setTimeout(resolve, 100));
            sv1.setDegree(db.get('currentDegree') + 10); // 0 - 180
            await new Promise(resolve => setTimeout(resolve, 100));
            sv1.setDegree(db.get('currentDegree') - 10); // 0 - 180
            await new Promise(resolve => setTimeout(resolve, 100));
            sv1.setDegree(db.get('currentDegree')); // 0 - 180
        });
    }

    mathAngle(currentAngle, direction) {
        // if direction 1 = +
        // if direction 0 = 1

        if (direction == 1) { // right +
            currentAngle += eachAngle;
            if (currentAngle >= 180) {
                direction = 0;
            }
        } else if (direction == 0) { // left -
            currentAngle -= eachAngle;
            if (currentAngle <= 0) {
                direction = 1;
            }
        }

        return {
            currentAngle,
            direction
        };
    }

}

module.exports = ServoController;