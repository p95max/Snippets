// let cost = Number(prompt("Item price:"));
// let n = Number(prompt("Item count:"));

// let number = 1;
//
// while (number <= n) {
//   console.log(`Count:${number} price:${number * cost}`)
//   number += 1;
// }


// for (let number = 1; number <= n; number++){
//     console.log(`Count:${number} price:${number * cost}`)
// }

// task 1
// function findLongestWord(words) {
//     let longestWord = words[0];
//     for (let word of words){
//         if (word.length > longestWord.length){
//             longestWord = word
//         }
//     }
//     return longestWord
// }
//
// const words = ["apple", "banana", "kiwi", "grapefruit"];
// console.log(findLongestWord(words));

// task 2

// function countVowels(str) {
//   let count = 0;
//   const vowels = "aeiou";
//   for (let char of str.toLowerCase()) {
//     if (vowels.includes(char)) {
//       count++;
//     }
//   }
//   return count;
// }
//
// console.log(countVowels("hello world"))

// task 3

// function sumObjectValues(obj) {
//   let sum = 0;
//   for (let key in obj) {
//       sum += obj[key];
//   }
//   return sum
// }
//
// const data = { a: 1, b: 2, c: 3 };
// console.log(sumObjectValues(data)); // 6

// task 4

// function createObjectFromKeys(arr) {
//   let result = {};
//   for (let word of arr) {
//       result[word] = word.length
//   }
//   return result;
// }
//
// const fruits = ["apple", "banana"];
// console.log(createObjectFromKeys(fruits));
// Ожидаемый результат: { apple: 5, banana: 6 }
