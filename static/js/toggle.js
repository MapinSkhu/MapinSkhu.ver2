// 대단위 version toggle
function outside(element) {
  // 이전 toggle 버튼
  var bigBefore = document.querySelector(".active_version");

  // 이전 toggle 버튼이 존재하지 않을 때 = 처음 toggle을 클릭했을 때
  if (bigBefore === null) {
    // 현재 클릭한 요소의 상태를 토글
    element.classList.toggle("active_version");

    // 현재 클릭한 버튼 아래에 위치한 left-line 정의
    var item = element.nextElementSibling;
    // left-line 내부 content 정의
    var content = item.querySelector(".version-items");
    content.style.opacity = "1";
    item.style.maxHeight = "1000px"; // final-line이 아닌 경우에는 다른 값으로 설정 가능

    // 이전 toggle 버튼 존재하며 그 버튼이 현재 선택 버튼과 "다를" 때
  } else if (bigBefore && bigBefore !== element) {
    var beforeItem = bigBefore.nextElementSibling;
    var beforeContent = beforeItem.querySelector(".version-items");
    // 이전 toggle 버튼 아래 left-line 길이 없애기
    if (beforeItem.classList.contains("before-final-line")) {
      beforeItem.style.maxHeight = "200px"; // final-line인 경우에만 0px로 설정
    } else {
      beforeItem.style.maxHeight = "50px"; // final-line이 아닌 경우에는 다른 값으로 설정 가능
    }
    beforeContent.style.opacity = "0";
    // 이전 toggle 버튼에서 "active_content" class 없애기
    bigBefore.classList.remove("active_version");

    // 현재 클릭한 요소의 상태를 토글
    element.classList.toggle("active_version");
    // 현재 클릭한 버튼 아래에 위치한 left-line 정의
    var item = element.nextElementSibling;
    // left-line 내부 content 정의
    var content = item.querySelector(".version-items");
    content.style.opacity = "1";
    item.style.maxHeight = "1000px"; // final-line이 아닌 경우에는 다른 값으로 설정 가능
  } else if (bigBefore && bigBefore === element) {
    var beforeItem = bigBefore.nextElementSibling;
    var beforeContent = beforeItem.querySelector(".version-items");
    // 이전 toggle 버튼 아래 left-line 길이 없애기
    if (beforeItem.classList.contains("before-final-line")) {
      beforeItem.style.maxHeight = "200px"; // final-line인 경우에만 0px로 설정
    } else {
      beforeItem.style.maxHeight = "50px"; // final-line이 아닌 경우에는 다른 값으로 설정 가능
    }
    beforeContent.style.opacity = "0";
    // 이전 toggle 버튼에서 "active_content" class 없애기
    bigBefore.classList.remove("active_version");
  }
}

// 소단위 version toggle
function collapse(element) {
  // 이전 toggle 버튼
  var before = document.querySelector(".active_content");

  // 이전 toggle 버튼이 존재하지 않을 때 = 처음 toggle을 클릭했을 때
  if (before === null) {
    // 현재 클릭한 toggle 버튼에 "active_content" class 추가하기
    element.classList.toggle("active_content");
    // 현재 클릭한 버튼 아래에 위치한 content 정의
    var content = element.nextElementSibling;

    // 현재 클릭한 toggle 버튼 아래에 위치한 content의 원래 길이만큼 드러내기
    content.style.maxHeight = content.scrollHeight + "px";
    content.style.borderTop = "none";
    content.style.borderBottom = "solid 1px #D8FDD1";
    content.style.marginBottom = "0px";

    // 이전 toggle 버튼 존재하며 그 버튼이 현재 선택 버튼과 "다를" 때
  } else if (before && before !== element) {
    // 이전 toggle 버튼 아래 content 길이 없애기
    before.nextElementSibling.style.maxHeight = null;
    before.nextElementSibling.style.borderTop = "solid 1px #e9e9e9";
    before.nextElementSibling.style.borderBottom = "none";
    before.nextElementSibling.style.marginBottom = "-1px";
    // 이전 toggle 버튼에서 "active_content" class 없애기
    before.classList.remove("active_content");

    // 현재 클릭한 toggle에 "active_content" class 추가하기
    element.classList.toggle("active_content");
    // 현재 클릭한 버튼 아래에 위치한 content 정의
    var content = element.nextElementSibling;

    // 현재 클릭한 toggle 버튼 아래에 위치한 content의 원래 길이만큼 드러내기
    content.style.maxHeight = content.scrollHeight + "px";
    content.style.borderTop = "none";
    content.style.borderBottom = "solid 1px #D8FDD1";
    content.style.marginBottom = "0px";

    // 이전 toggle 버튼 존재하며 그 버튼이 현재 선택 버튼과 "같을" 때 = 같은 버튼 2번 클릭
  } else if (before && before === element) {
    // 이전(=현재) toggle 버튼 아래 content 길이 없애기
    before.nextElementSibling.style.maxHeight = null;
    before.nextElementSibling.style.borderTop = "solid 1px #e9e9e9";
    before.nextElementSibling.style.borderBottom = "none";
    before.nextElementSibling.style.marginBottom = "-1px";
    // 이전(=현재) toggle 버튼에서 "active_content" class 없애기
    before.classList.remove("active_content");
  }
}
