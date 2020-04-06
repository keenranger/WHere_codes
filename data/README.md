# 데이터들 분류

## 0344
* e1 : L1 반시계로 한바퀴 
* e2 : L2 시계로 한바퀴

## 0401
* 0401t2 roll pitch 보정을 위한 90도 회전 테스트 - 제자리

## headingtest
* heading1 : 264걸음 L1 한바퀴 + 1/4
* heading2 : 책상 위 가만히 
* heading3: 책상 위 두바퀴 
* heading4: L1 한바퀴(반시계)
* heading5 : L1 두바퀴(시계)

# 찾는 방법1
각각의 시나리오 별로 state를 만들고, state별로 다른 방법으로 peak/valley를 detect한다
# 찾는 방법2
모든 시나리오에 대응할 수 있는(최소한 norm값을 사용했기에 orientation tilting에 의한 영향을 적게 받을 수 있다.) peak/valley detecting 알고리즘을 찾는다.