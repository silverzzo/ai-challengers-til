---
title: "(Sample) HTML"
date: 2026-07-13
---

# (Sample) HTML

## 📝 오늘 배운 내용 요약

1. **HTML 시맨틱 태그의 이해와 활용**
- semantic tag가 SEO와 웹 접근성에 미치는 영향 학습
- header, nav, main, aside, section, article, footer 등 각 태그의 적절한 사용법
- div와 시맨틱 태그의 차이점과 사용해야 하는 상황 구분
```html
html
Copy
<header>
  <h1>웹사이트 제목</h1>
  <nav>
    <ul>
      <li><a href="#home">홈</a></li>
      <li><a href="#about">소개</a></li>
    </ul>
  </nav>
</header>
```

2. **CSS Float vs Flexbox**
- Float의 한계점과 Flexbox의 등장 배경
- Flexbox 주요 속성 실습
- flex-direction: row, column 차이
- justify-content: space-between vs space-around
- align-items vs align-content
- 실제 레이아웃 구현 시 발생한 이슈와 해결 방법
```css
css
Copy
.container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}
```

3. **CSS Float vs Flexbox**
- Float의 한계점과 Flexbox의 등장 배경
- Flexbox 주요 속성 실습
- flex-direction: row, column 차이
- justify-content: space-between vs space-around
- align-items vs align-content
- 실제 레이아웃 구현 시 발생한 이슈와 해결 방법
```css
css
Copy
.container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}
```

## 💭 오늘의 회고

1. **배운 점**
- 시맨틱 태그를 사용하면서 HTML 구조가 더 명확해지고 코드 가독성이 높아짐을 체감
- Flexbox로 해결할 수 있는 레이아웃이 생각보다 많다는 것을 알게 됨
- 크롬 개발자 도구의 Elements 탭을 적극 활용하니 디버깅이 수월했음
2. **어려운 점/개선할 점**
- Flexbox의 align-self 속성 활용이 아직 서툴러서 추가 학습 필요
- 시맨틱 태그 중 section과 article의 사용 기준이 모호함
- 실습 시간에 너무 완벽을 추구하다가 시간 관리를 못함
3. **액션 플랜**
- [ ] MDN 문서에서 section vs article 차이점 학습
- [ ] Flexbox 실전 예제 3개 만들어보기
- [ ] 내일까지 과제 레이아웃 완성하기
- [ ] 코드 리뷰 받은 부분 수정
4. **함께 나누고 싶은 점**
- Flexbox 학습에 도움된 사이트: Flexbox Froggy
- 페어 프로그래밍하면서 알게 된 VS Code 유용한 단축키들
- 다른 분들은 시맨틱 태그 선택 기준이 궁금함
## 📚 참고자료

- [HTML5 시맨틱 요소와 사용법](http://xn--9y2bo82b/)
- [CSS Flex 완벽 가이드](http://xn--9y2bo82b/)
- [오늘 수업 필기 노트](http://xn--9y2bo82b/)
## 🔍 내일 학습 예정

- Grid 레이아웃 시스템
- 반응형 웹 디자인 기초
- 미디어 쿼리 활용법

