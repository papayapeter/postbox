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

const uint8_t GPIO_UNLOCK_IN     = 18;
const uint8_t GPIO_MAIL_OUT      = 19;
const uint8_t GPIO_UNLOCKED_OUT  = 20;
const uint8_t GPIO_TOUCHED_OUT   = 21;

// objects ---------------------------------------------------------------------
// timers
Metro touch_timer(50);

// debouncers
Bounce beam        = Bounce();
Bounce door_switch = Bounce();

// servos
PWMServo door_servo;
PWMServo flag_servo;

// variables -------------------------------------------------------------------

// touch
int32_t touch_calibrated;
int32_t  touch_deviation;

bool last_touched = true;

// door
bool door_open = true;

// flag (mail)
bool mail_in = false;

// settings --------------------------------------------------------------------
const uint8_t door_open_pos   = 180;
const uint8_t door_closed_pos = 174;
const uint8_t flag_up_pos     = 80;
const uint8_t flag_down_pos   = 170;

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
  // Serial.begin(9600);

  // set up pins
  pinMode(LED, OUTPUT);

  pinMode(GPIO_UNLOCK_IN, INPUT);
  pinMode(GPIO_MAIL_OUT, OUTPUT);
  pinMode(GPIO_UNLOCKED_OUT, OUTPUT);
  pinMode(GPIO_TOUCHED_OUT, OUTPUT);

  // set up debounced pins
  beam.attach(BEAM, INPUT_PULLUP);
  beam.interval(10);

  door_switch.attach(DOOR_SWITCH, INPUT_PULLUP);
  door_switch.interval(10);

  // set up servos
  flag_servo.attach(FLAG_SERVO);
  door_servo.attach(DOOR_SERVO);

  flag_servo.write(flag_down_pos);
  door_servo.write(door_open_pos);

  // calibrate the touch
  touchCalibrate(DOOR_TOUCH, LED, 100, 50, touch_calibrated, touch_deviation);
}

// loop ------------------------------------------------------------------------
void loop()
{
  // read the touch
  if (touch_timer.check())
  {
    if (touchReadCalibrated(DOOR_TOUCH, touch_calibrated, touch_deviation))
    {
      if (!last_touched)
        // Serial.println("grabbed");

      last_touched = true;

      // send to raspberry pi
      digitalWrite(GPIO_TOUCHED_OUT, HIGH);
    }
    else
    {
      if (last_touched)
        // Serial.println("let go");

      last_touched = false;

      // send to raspberry pi
      digitalWrite(GPIO_TOUCHED_OUT, LOW);
    }
  }

  // check beam sensor
  beam.update();

  if (beam.fell())
  {
    // Serial.println("in beam");

    mail_in = true;

    // send to raspberry pi
    digitalWrite(GPIO_MAIL_OUT, HIGH);
  }
  else if (beam.rose())
  {
    // Serial.println("out of beam");

    mail_in = false;

    // send to raspberry pi
    digitalWrite(GPIO_MAIL_OUT, LOW);
  }

  // check door switch
  door_switch.update();

  if (door_switch.fell() && door_open && !digitalRead(GPIO_UNLOCK_IN))
  {
    // Serial.println("door closed");

    // lock door
    door_open = false;

    // send to raspberry pi
    digitalWrite(GPIO_UNLOCKED_OUT, LOW);

    // raise or lower flag
    if (mail_in)
      flag_servo.write(flag_up_pos);
    else
      flag_servo.write(flag_down_pos);
  }
  else if (door_switch.rose())
  {
    // Serial.println("door opened");
  }

  // check raspberry pi input
  if (digitalRead(GPIO_UNLOCK_IN) && !door_open)
  {
    // Serial.println("door unlocked");

    // open door
    door_open = true;

    // send to raspberry pi
    digitalWrite(GPIO_UNLOCKED_OUT, HIGH);
  }

  // servos
  if (door_open)
    door_servo.write(door_open_pos);
  else
    door_servo.write(door_closed_pos);
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
  static int32_t touch_stack[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

  // push everything back and drop last values
  for (uint8_t i = 0; i < 10 - 1; i ++)
  {
    touch_stack[i + 1] = touch_stack[i];
  }

  // put new value in the front
  touch_stack[0] = touchRead(pin);

  // calculate average
  int32_t average = 0;
  for (uint8_t i = 0; i < 10; i++)
  {
    average += touch_stack[i];
  }
  average /= 10;

  // get result
  return abs(average - base) > abs(deviation / 6);
}
