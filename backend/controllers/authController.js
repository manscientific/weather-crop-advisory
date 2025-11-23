import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import Farmer from "../models/Farmer.js";

const generateToken = (id) => {
  return jwt.sign({ id }, process.env.JWT_SECRET, {
    expiresIn: "7d",
  });
};

export const registerFarmer = async (req, res) => {
  try {
    const { name, email, password, location } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({ message: "Please fill all fields" });
    }

    const existing = await Farmer.findOne({ email });
    if (existing) {
      return res.status(400).json({ message: "Farmer already exists" });
    }

    const salt = await bcrypt.genSalt(10);
    const hashed = await bcrypt.hash(password, salt);

    const farmer = await Farmer.create({
      name,
      email,
      password: hashed,
      location,
    });

    return res.status(201).json({
      _id: farmer._id,
      name: farmer.name,
      email: farmer.email,
      location: farmer.location,
      token: generateToken(farmer._id),
    });
  } catch (error) {
    console.error("Register error:", error.message);
    return res.status(500).json({ message: "Server error" });
  }
};

export const loginFarmer = async (req, res) => {
  try {
    const { email, password } = req.body;

    const farmer = await Farmer.findOne({ email });
    if (!farmer) {
      return res.status(400).json({ message: "Invalid credentials" });
    }

    const isMatch = await bcrypt.compare(password, farmer.password);
    if (!isMatch) {
      return res.status(400).json({ message: "Invalid credentials" });
    }

    return res.json({
      _id: farmer._id,
      name: farmer.name,
      email: farmer.email,
      location: farmer.location,
      token: generateToken(farmer._id),
    });
  } catch (error) {
    console.error("Login error:", error.message);
    return res.status(500).json({ message: "Server error" });
  }
};

export const getProfile = async (req, res) => {
  // req.farmer is set by middleware
  return res.json(req.farmer);
};
