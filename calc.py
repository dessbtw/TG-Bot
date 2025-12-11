def RaschetM(age, weight, height):
    return 10 * weight + 6.25 * height - 5 * age + 5

def RaschetW(age, weight, height):
    return 10 * weight + 6.25 * height - 5 * age - 161

def Activ(kall, act):
    if act == "1":
        kall *= 1.2
    elif act == "2":
        kall *= 1.375
    elif act == "3":
        kall *= 1.55
    elif act == "4":
        kall *= 1.725
    elif act == "5":
        kall *= 1.9
    else:
        raise ValueError("Неверная активность")
    return kall
            
def Poxyd(kall, weight):
    kall -= 375
    proteins = [weight * 2, weight * 2.4]
    fats = [weight * 0.7, weight * 0.9]

    return kall, proteins, fats

def Uderj(kall, weight):
    proteins = [weight * 2, weight * 2.4]
    fats = [weight * 0.7, weight * 0.9]

    return kall, proteins, fats

def Nabor(kall, weight):
    kall += 375
    proteins = [weight * 2, weight * 2.4]
    fats = [weight * 0.7, weight * 0.9]

    return kall, proteins, fats

def Yglevodi(kall, proteins, fats):
    carbohydrates = [(kall - (proteins[0] * 4) - (fats[0] * 9))/4, (kall - (proteins[1] * 4) - (fats[1] * 9))/4]
    return carbohydrates

def Output(gender, age, weight, height, activity, goal):
    if gender == "🟦 Мужчина":
        kall = RaschetM(age, weight, height)
    elif gender == "🩷 Женщина":
        kall = RaschetW(age, weight, height)
    else:
        raise ValueError("Ошибка в выборе пола!")

    kall = Activ(kall, str(activity))

    if goal == "lose":
        kall, proteins, fats = Poxyd(kall, weight)
    elif goal == "keep":
        kall, proteins, fats = Uderj(kall, weight)
    elif goal == "gain":
        kall, proteins, fats = Nabor(kall, weight)
    else:
        raise ValueError("Неверная цель")

    carbohydrates = Yglevodi(kall, proteins, fats)

    print("Калории:", int(kall))
    print(f"Белки от {int(proteins[0])} г до {int(proteins[1])} г")
    print(f"Жиры от {int(fats[0])} г до {int(fats[1])} г")
    print(f"Углеводы - все остальное. На них акцент не делаем, т.к. это просто энергия. \n"
      f"Но выходит примерно от {int(carbohydrates[1])} г до {int(carbohydrates[0])} г")
    
    return {
        "kcal": int(kall),
        "proteins": proteins,
        "fats": fats,
        "carbs": carbohydrates
    }

def BMI(weight, height):
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    
    if bmi <= 16:
        category = "выраженный дефицит массы тела 🦴"
    elif 16 < bmi <= 18.5:
        category = "небольшой дефицит массы тела 🪶"
    elif 18.5 < bmi <= 25:
        category = "норма 🙂"
    elif 25 < bmi <= 30:
        category = "небольшой избыток массы тела 🍫"
    elif 30 < bmi <= 35:
        category = "избыток массы тела 🍔"
    elif 35 < bmi <= 40:
        category = "ожирение второй степени ⚠️"
    else:
        category = "ожирение третьей степени (морбидное) 🛑"
    
    return round(bmi, 1), category

