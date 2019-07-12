// libraries -------------------------------------------------------------------
#include <Metro.h>
#include <Bounce2.h>
#include <PWMServo.h>

// pins ------------------------------------------------------------------------
const uint8_t LED         = 13;
const uint8_t BEAM        = 16;
const uint8_t DOOR_SWITCH = 0;
const uint8_t DOOR_SERVO  = 3;
const uint8_t FLAG_SERVO  = 4;
const uint8_t DOOR_TOUCH  = 15;

// objects ---------------------------------------------------------------------
// timers
Metro servo_timer(50);
Metro touch_timer(50);

// debouncers
Bounce beam        = Bounce();
Bounce door_switch = Bounce();

// servos
PWMServo door_servo;
PWMServo flag_servo;

// variables -------------------------------------------------------------------
// servos
uint8_t flag_servo_pos = 0;
int8_t  flag_servo_dir = 1;

// touch
int32_t touch_calibrated;
int32_t  touch_deviation;

// functions -------------------------------------------------------------------
/**
 * @brief   calibrates the touch pin
 *
 * first it reads value when nobody touches. When led turns on,
 * it reads the touch value
 *
 * @param   interval  interval between samples in milliseconds
 * @param   base      pointer to the variable, of the calibrated no touch value
 * @param   deviation pointer to the variable, of the deviation when touched
 */
void touchCalibrate(uint8_t pin, uint8_t led_pin, uint8_t samples, uint8_t interval,
                    int32_t& base, int32_t& deviation);
/**
 * @brief   reads from the calibrated touch pin
 */
bool touchReadCalibrated(uint8_t pin, int32_t base, int32_t deviation);

// setup -----------------------------------------------------------------------
void setup()
{
  // debug
  Serial.begin(9600);

  // set up pins
  pinMode(LED, OUTPUT);

  // set up debounced pins
  beam.attach(BEAM, INPUT_PULLUP);
  beam.interval(10);

  door_switch.attach(DOOR_SWITCH, INPUT_PULLUP);
  door_switch.interval(50);

  // set up servos
  flag_servo.attach(FLAG_SERVO);
  door_servo.attach(DOOR_SERVO);

  // write default position
  flag_servo.write(180);
  door_servo.write(175);

  // calibrate the touch
  touchCalibrate(DOOR_TOUCH, LED, 100, 50, touch_calibrated, touch_deviation);

  // debug
  Serial.println("base " + String(touch_calibrated) +
               "\tdeviation " + String(touch_deviation));
}

// loop ------------------------------------------------------------------------
void loop()
{
  // read the touch
  if (touch_timer.check())
    Serial.println(touchReadCalibrated(DOOR_TOUCH, touch_calibrated, touch_deviation));

  // move the servo
  if (servo_timer.check())
  {
    flag_servo_pos += flag_servo_dir;

    if (flag_servo_pos >= 180)
    {
      flag_servo_dir = -1;
      Serial.println("servo 180");
    }
    else if (flag_servo_pos <= 0)
    {
      flag_servo_dir = 1;
      Serial.println("servo 0");
    }

    flag_servo.write(flag_servo_pos);
  }

  // check beam sensor
  beam.update();

  if (beam.fell())
    Serial.println("in beam");
  else if (beam.rose())
    Serial.println("out of beam");

  // check door switch
  door_switch.update();

  if (door_switch.fell())
    Serial.println("door closed");
  else if (door_switch.rose())
    Serial.println("door opened");
}

// functions -------------------------------------------------------------------
void touchCalibrate(uint8_t pin, uint8_t led_pin, uint8_t samples, uint8_t interval,
                    int32_t& base, int32_t& deviation)
{
  // turn led off
  digitalWrite(led_pin, LOW);

  // collect data
  base = 0;
  for (uint8_t i = 0; i < samples; i++)
  {
    base += touchRead(pin);
    delay(interval);
  }

  // get average
  base /= samples;

  // turn led on & wait 5 seconds
  digitalWrite(led_pin, HIGH);
  delay(5000);

  deviation = 0;
  for (uint8_t i = 0; i < samples; i++)
  {
    deviation += touchRead(pin);
    delay(interval);
  }

  // get average & relative value
  deviation /= samples;
  deviation -= base;

  // turn led off
  digitalWrite(led_pin, LOW);
}
bool touchReadCalibrated(uint8_t pin, int32_t base, int32_t deviation)
{
  // stack to store current & previous touch values
  static uint32_t touch_stack[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

  // push everything back and drop last values
  for (uint8_t i = 0; i < 10 - 1; i ++)
  {
    touch_stack[i + 1] = touch_stack[i];
  }

  // put new value in the front
  touch_stack[0] = touchRead(pin);

  // calculate average
  uint32_t average = 0;
  for (uint8_t i = 0; i < 10; i++)
  {
    average += touch_stack[i];
  }
  average /= 10;

  // get result
  return abs(average - base) > abs(deviation / 2);
}
